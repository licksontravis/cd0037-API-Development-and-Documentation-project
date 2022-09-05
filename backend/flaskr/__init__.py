from crypt import methods
from datetime import datetime
from http.client import responses
import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. 
    Delete the sample route after completing the TODOs
    """
    CORS(app)

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):      
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods","GET,PUT,POST,DELETE,OPTIONS"
        )
        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route("/categories")
    def get_categories():
        try:
            categories = {cat.id : cat.type for cat in Category.query.all()}
            return jsonify({
                "categories": categories
            })
        except:
            abort(422)

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route("/questions")
    def get_questions():
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)

        if len(current_questions) == 0:
            abort(404)
        categories = {cat.id : cat.type for cat in Category.query.all()}
        return jsonify({
            "questions": current_questions,
            "total_questions": len(Question.query.all()),
            "categories": categories,
            "current_category": None
        })
        
    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
        try:
            question = Question.query.filter(Question.id == question_id).one_or_none()
            if question is None:
                abort(404)
            
            question.delete()
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)
            categories = {cat.id : cat.type for cat in Category.query.all()}
            return jsonify({
                "questions": current_questions,
                "total_questions": len(Question.query.all()),
                "current_category": None,
                "categories": categories
            })
        except:
            abort(422)

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route("/questions", methods=["POST"])
    def create_question():
        body = request.get_json()
        new_question = body.get("question", None)
        new_answer = body.get("answer",None)
        new_difficulty = body.get("difficulty",None)
        category = body.get("category",None)
        search = body.get("searchTerm")
        try:
            if search:
                selection = Question.query.order_by(Question.id).filter(
                    Question.question.ilike("%{}%".format(search))
                )
                current_questions = paginate_questions(request, selection)
                return jsonify({
                    "questions": current_questions,
                    "total_questions": len(Question.query.all()),
                    "current_category": None,
                })

            else:
                question = Question(new_question, new_answer, category, new_difficulty)
                question.insert()
                return jsonify()
        except:
            abort(422)
    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route("/categories/<int:category_id>/questions")
    def get_questions_by_category(category_id):
        try:
            selection = Question.query.filter(Question.category == category_id).order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)

            if len(current_questions) == 0:
                abort(404)
            return jsonify({
                "questions": current_questions,
                "total_questions": len(current_questions),
                "current_category": None
            })
        except:
            abort(422)
    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route("/quizzes", methods=["POST"])
    def get_quiz_question():
        body = request.get_json()
        previous_questions_id_list = body.get("previous_questions", None)

        quiz_category = body.get("quiz_category",None)
        try:
            if quiz_category["id"] == 0: # ===> We click on "ALL"
                elligible_questions = Question.query.all()
            else: # ===> We select one category (not "ALL")
                current_cat = Category.query.get(int(quiz_category["id"]))
                if len(previous_questions_id_list) == 0: # ===> We just started playing (previous question lit is Empty)
                    elligible_questions = Question.query.filter(Question.category==current_cat.id).all()
                else:
                
                    elligible_questions = Question.query.filter(db.and_(
                            Question.id.notin_(previous_questions_id_list),
                            Question.category==current_cat.id
                            )
                        ).all()
            if elligible_questions:
                random_question_id = random.choice([q.id for q in elligible_questions])
                next_question = Question.query.get(random_question_id)
                return jsonify({
                    "question":{
                        "id": next_question.id,
                        "question": next_question.question,
                        "answer": next_question.answer,
                        "difficulty": next_question.difficulty,
                        "category": next_question.category
                    }
                })
            else: # ===> We finish anwser all questions for the select category
                return jsonify({
                    "question":None
                })
        except:
            abort(422)
    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({
                "success": False, 
                "error": 404, 
                "message": "resource not found"
            }),
            404,
        )

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({
                "success": False, 
                "error": 422, 
                "message": "unprocessable"
            }),
            422,
        )

    @app.errorhandler(500)
    def server_error(error):
        return (
            jsonify({
                "success": False, 
                "error": 500, 
                "message": "server error"
            }),
            500,
        )        

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False, 
            "error": 400, 
            "message": "bad request"
        }), 400

    return app

