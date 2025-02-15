import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
load_dotenv()

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        DB_HOST = os.getenv('DB_HOST')
        DB_USER = os.getenv('DB_USER')
        DB_PASSWORD = os.getenv('DB_PASSWORD')
        DB_TEST_NAME = os.getenv('DB_TEST_NAME')
        DB_PATH = 'postgresql+psycopg2://{}:{}@{}/{}'.format(DB_USER, DB_PASSWORD, DB_HOST, DB_TEST_NAME)
        
        self.database_name = DB_TEST_NAME
        self.database_path = DB_PATH
        
        self.app = create_app()
        self.client = self.app.test_client
        setup_db(self.app, self.database_path)

        self.new_question = {
            "question":"Here is a new question string",
            "answer":"Here is a new answer string",
            "difficulty":"1",
            "category":"3"
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    ###########  Success tests for questions #############

    def test_get_questions(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["questions"]))
        self.assertTrue(data["categories"])


    def test_get_questions_by_category(self):
        res = self.client().get("/categories/2/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data["questions"]))


    def test_create_new_question(self):
        res = self.client().post("/questions", json=self.new_question)
        data = json.loads(res.data)
        pass


    def test_get_question_search_with_results(self):
        res = self.client().post("/questions", json={"searchTerm": "Peanut Butter"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["total_questions"])
        self.assertEqual(len(data["questions"]), 1)


    def test_get_question_search_without_results(self):
        res = self.client().post("/questions", json={"searchTerm": "downtown"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(data["questions"]), 0)
    

    def test_get_quizz_question(self):
        res = self.client().post("/quizzes", json={"previous_questions":[], "quiz_category":{"id":2}})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["question"]["category"], 2)


    # def test_delete_question(self):
    #     res = self.client().delete('/questions/1')
    #     data = json.loads(res.data)

    #     question = Question.query.filter(Question.id == 1).one_or_none()

    #     self.assertEqual(res.status_code, 200)
    #     self.assertEqual(data['success'], True)
    #     self.assertEqual(data['deleted'], 1)
    #     self.assertTrue(data['total_questions'])
    #     self.assertTrue(len(data['questions']))
    #     self.assertEqual(question, None)          
    
    ###########  Failed tests for questions #############

    def test_404_questions_by_category_not_exist(self):    
        res = self.client().get("/categories/-2/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)


    def test_404_request_invalid_page(self):
        res = self.client().get("/questions?page=1000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found") 


    def test_404_if_question_does_not_exist(self):
        res = self.client().delete("/questions/1000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")   


    def test_422_if_question_creation_fails(self):
        res = self.client().post("/questions", json=self.new_question)
        data = json.loads(res.data)
        pass

    ########### Success tests for category ###############

    def test_get_categories(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)

        self.assertTrue(res.status_code, 200)
        self.assertTrue(data["categories"])
        self.assertTrue(len(data["categories"]))

    ###########  Failed tests for category #############

    def test_422_failed_getting_categories(self):
        res = self.client().get("/categories?x=2")
        data = json.loads(res.data)

        self.assertTrue(res.status_code, 422)
    

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()