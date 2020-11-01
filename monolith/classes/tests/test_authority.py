from monolith.app import create_app
from monolith.database import db, User
from monolith.classes.tests.utils import add_random_users, add_random_visits_to_place, delete_random_users, mark_random_guy_as_positive, random_datetime_in_range, visit_random_places
from monolith.classes.authority_frontend import mark_user, search_user
from monolith.classes.authority_backend import unmark_all
import unittest, random
from datetime import datetime, timedelta


class TestAuthority(unittest.TestCase):
    def setUp(self):
        self.rand = [random.randint(1, 9) for i in range(0, 5)]
        self.app = create_app()
        #remove any test user from the db
        delete_random_users(self.app)
        self.user_id = 0

    def test_markuser(self):
        add_random_users(1, self.app)
        with self.app.app_context():
            # get the id and ensure is not positive
            user = User.query.filter_by(email='test').first()
            self.assertIsNotNone(user)
            self.assertFalse(user.is_positive)
            self.assertIsNone(user.reported_positive_date)

            self.user_id = user.id
            error_message = mark_user(user.id)
            self.assertEqual(error_message, '')

            #Check he/she has been really marked as positive
            after_mark = User.query.filter_by(id=user.id).first()
            self.assertIsNotNone(after_mark)
            self.assertTrue(after_mark.is_positive)
            self.assertIsNotNone(after_mark.reported_positive_date)

            #Try to mark a user twice
            error_message = mark_user(user.id)
            self.assertNotEqual(error_message, '')

            delete_random_users(self.app)

    def test_unmarkuser(self):
        with self.app.app_context():
            add_random_users(1, self.app)
            quarantine_days = random.randrange(1, 20)
            
            # get the id and ensure is not positive
            user = User.query.filter_by(email='test').first()
            self.assertIsNotNone(user)
            usrid = user.id
            
            #Marks as positive
            user.is_positive = True
            user.reported_positive_date = datetime.now() - timedelta(days=quarantine_days+1)
            
            #Call the function
            unmark_all(quarantine_days)

            #Check he/she has been really unmarked
            after_mark = User.query.filter_by(id=usrid).first()
            self.assertIsNotNone(after_mark)
            self.assertFalse(after_mark.is_positive)
            self.assertIsNone(after_mark.reported_positive_date)
            delete_random_users(self.app)

    def test_search_user(self):
        with self.app.app_context():
            # Add a user
            user = User(email='test@test.com', firstname=f'test_search', lastname=f'test_search', 
            password='test', dateofbirth=datetime.now(), is_active=bool(random.randrange(0, 2)),
            is_admin=False, is_positive=False, ssn='TESTCF95M00A123A', phone_number='3331231234')
            print(f"Adding user {user}")
            db.session.add(user)
            db.session.commit()

            # get the id and ensure is not positive
            user = User.query.filter_by(ssn='TESTCF95M00A123A').first()
            self.assertIsNotNone(user)
            usrid = user.id

            filter_mail = User(email='test@test.com')
            filter_ssn = User(ssn='TESTCF95M00A123A')
            filter_phone = User(phone_number='3331231234')
            filter_absent_user = User(phone_number='345677890')
            
            user, message = search_user(filter_mail)
            self.assertIsNotNone(user)
            self.assertEqual(user.id, usrid)

            user, message = search_user(filter_ssn)
            self.assertIsNotNone(user)
            self.assertEqual(user.id, usrid)

            user, message = search_user(filter_phone)
            self.assertIsNotNone(user)
            self.assertEqual(user.id, usrid)

            user, message = search_user(filter_absent_user)
            self.assertIsNone(user)

            # Delete the user
            delete_query = User.__table__.delete().where(User.ssn == 'TESTCF95M00A123A')
            db.session.execute(delete_query)
            db.session.commit()

    def clean(self):
        delete_random_users(self.app)


if __name__ == "__main__":
    unittest.main()