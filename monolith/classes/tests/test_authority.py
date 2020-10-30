from monolith.app import create_app
from monolith.database import db, User
from monolith.classes.tests.utils import add_random_users, add_random_visits_to_place, delete_random_users, mark_random_guy_as_positive, random_datetime_in_range, visit_random_places
from monolith.classes.authority_frontend import mark_user
from monolith.classes.authority_backend import unmark_user, unmark_all
import unittest, random


class TestAuthority(unittest.TestCase):
    def setUp(self):
        self.rand = [random.randint(1, 9) for i in range(0, 5)]
        self.app = create_app()
        #remove any test user from the db
        delete_random_users(self.app)

    def test_markuser(self):
        add_random_users(1, self.app)
        with self.app.app_context():
            # get the id and ensure is not positive
            user = User.query.filter_by(email='test').first()
            self.assertIsNotNone(user)
            self.assertFalse(user.is_positive)
            self.assertIsNone(user.reported_positive_date)

            error_message = mark_user(user.id)
            self.assertEqual(error_message, '')

            #Check he/she has been really marked as positive
            after_mark = User.query.filter_by(id=user.id).first()
            self.assertIsNotNone(after_mark)
            self.assertTrue(after_mark.is_positive)
            self.assertIsNotNone(after_mark.reported_positive_date)

    def test_double_markuser(self):
        with self.app.app_context():
            # get the id and ensure is not positive
            user = User.query.filter_by(email='test').first()
            self.assertIsNotNone(user)

            error_message = mark_user(user.id)
            self.assertNotEqual(error_message, '')

    def test_unmarkuser(self):
        pass

    def clean(self):
        delete_random_users(self.app)


if __name__ == "__main__":
    unittest.main()