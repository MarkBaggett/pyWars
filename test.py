import unittest
import pyWars


class TestSolution(unittest.TestCase):

    def test_exercise_init(self):
        d = pyWars.exercise("http://127.0.0.1:10000")
        d.save_config()

    def test_questions(self):
        d = pyWars.exercise("http://127.0.0.1:10000")
        d.login("markbqa1","Mypassword1")
        for q in d.names:
            d.question(q)

    def test_673_questions(self):
        d = pyWars.exercise("http://127.0.0.1:10000")
        d.login("markbqa2","Mypassword1")
        for q in d.names:
            d.question(q)


    def test_data(self):
        d = pyWars.exercise("http://127.0.0.1:10000")
        d.login("markbqa1","Mypassword1")
        for q in d.names:
            d.data(q)

    def test_attachment(self):
        d = pyWars.exercise("http://127.0.0.1:10000")
        d.login("markbqa1","Mypassword1")
        for q in d.names:
            d.attachment(q)
        d.login("markbqa2","Mypassword1")
        for q in d.names:
            d.attachment(q)


if __name__ == '__main__':
    unittest.main()

