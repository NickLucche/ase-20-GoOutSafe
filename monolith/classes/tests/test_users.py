from sqlalchemy.sql.functions import random
from monolith.classes.tests.utils import setup_for_test, user_data, clear_password, restaurant_data
from monolith.classes.exceptions import DatabaseError, FormValidationError
from monolith.classes.user import edit_user_data, new_operator, new_user, users_view

from monolith.views import blueprints

from monolith.auth import login_manager
from monolith.views.users import create_user
from monolith.forms import OperatorForm, UserForm, UserProfileEditForm
from operator import add
import unittest, datetime, logging

from flask.app import Flask
from monolith.app import create_app
from monolith.database import Restaurant, User, db
import random
class TestUsers(unittest.TestCase):

    def test_usersview(self):
        app = setup_for_test()
        with app.app_context():
            if not users_view():
                return False
            return True

    def test_createuser(self):
        app = setup_for_test()
        # tests the creation of a new user with data validation

        with app.test_request_context():
            form = UserForm(**user_data)
            new_user(form, __submit=False, __password=clear_password)
            try:
                new_user(form, __submit=False, __password=clear_password)
                return False
            except DatabaseError:
                try:
                    new_user(form)
                    return False
                except FormValidationError:
                    return True

    def test_edituser(self):
        app = setup_for_test()

        # tests the editing of the profile information of an user
        new_data = {'email':'email' + str(random.randint(0, 1000)) + 'email.com', 'phone':'3333333333'}

        with app.test_request_context():
            form = UserForm(**user_data)
            u = new_user(form, __submit=False, __password=clear_password)
            form = UserProfileEditForm(**new_data)
            edit_user_data(form, u.id, __submit=False)
            try:
                edit_user_data(form, u.id)
                return False
            except FormValidationError:
                return True

    def test_createoperator(self):
        app = setup_for_test()
        # tests the creation of a new operator/restaurant with data validation

        data = {**user_data, **restaurant_data}

        with app.test_request_context():
            form = OperatorForm(**data)
            new_operator(form, __submit=False, __password=clear_password)
            try:
                new_operator(form, __submit=False, __password=clear_password)
                return False
            except DatabaseError:
                try:
                    new_operator(form)
                    return False
                except FormValidationError:
                    return True
            
if __name__ == "__main__":
    unittest.main()