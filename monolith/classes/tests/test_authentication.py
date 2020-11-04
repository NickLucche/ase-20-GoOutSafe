from monolith.classes.exceptions import UserNotInDB
from monolith.classes.authentication import authenticate_user
from monolith.classes.user import new_user
from monolith.forms import LoginForm, UserForm
from monolith.classes.tests.utils import setup_for_test, user_data, clear_password
import unittest

class TestAuth(unittest.TestCase):
    def test_authentication(self):
        app = setup_for_test()
        with app.test_request_context():
            form = UserForm(**user_data)
            u = new_user(form, __submit=False, __password=clear_password)
            form = LoginForm()
            form.email.data = u.email
            form.password.data = clear_password
            authenticate_user(form, __submit=False)
            try:
                authenticate_user(form)
                return False
            except:
                try:
                    form.email.data = 'notpresent@email.com'
                    authenticate_user(form, __submit=False)
                    return False
                except UserNotInDB:
                    return True