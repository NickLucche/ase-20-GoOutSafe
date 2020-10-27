from monolith.app import create_app
from monolith.database import db, User
import unittest, random


class TestAddUser(unittest.TestCase):
    def setUp(self):
        self.rand = [random.randint(1, 9) for i in range(0, 5)]
        self.app = create_app()

    def test_adduser(self):
        with self.app.app_context():
            for x in self.rand:
                rand_usr = User(firstname=f"user{x}",
                                lastname=f"useroni{x}",
                                email=f"user{x}@example.com")
                db.session.add(rand_usr)
                db.session.commit()
            for x in self.rand:
                rand_usr = db.session.query(User).filter_by(
                    lastname=f"useroni{x}").first()
                self.assertEqual(rand_usr.lastname, f"useroni{x}")

    def test_deluser(self):
        with self.app.app_context():
            for x in self.rand:
                garbage_usr = User(firstname=f"deleteme{x}",
                                   lastname=f"garbage{x}",
                                   email=f"garbage{x}@example.com")
                db.session.add(garbage_usr)
                db.session.commit()
            for x in self.rand:
                garbage_usr = db.session.query(User).filter_by(
                    lastname=f"garbage{x}").first()
                db.session.delete(garbage_usr)
                db.session.commit()
            for x in self.rand:
                garbage_usr = db.session.query(User).filter_by(
                    lastname=f"garbage{x}").first()
                self.assertIsNone(garbage_usr)


if __name__ == "__main__":
    unittest.main()
