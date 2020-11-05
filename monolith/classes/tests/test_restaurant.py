from monolith.classes.exceptions import FormValidationError
from monolith.classes.user import new_operator, new_user
from monolith.forms import OperatorForm, RestaurantProfileEditForm, UserForm
from monolith.classes.tests.utils import *
import unittest
from monolith.classes.restaurant import add_review, edit_restaurant, update_review
import os

class TestRestaurant(unittest.TestCase):
    
    def test_edit(self):
        app = setup_for_test()
        # adds a new restaurant/operator and calls the "edit_tables" method on it
        # if a database error happen an SQLAlchemy exception should be raised
        # making the test fail
        data = {**user_data, **restaurant_data}
        request = {'table_1' : 4,
                  'table_2' : 7,
                  'table_3' : 11}
        with app.test_request_context():
            operator_form = OperatorForm(**data)
            edit_form = RestaurantProfileEditForm(**data)
            operator = new_operator(operator_form, __submit=False)
            edit_restaurant(edit_form, request, operator.restaurant_id, __submit=False)
            try:
                edit_restaurant(edit_form, request, operator.restaurant_id)
                return False
            except FormValidationError:
                return True

    def test_addreview(self):
        app = setup_for_test()

        # adds a new restaurant/operator and and a new user and calls the
        # method "add_review" to add a review for that restaurant
        # if a database error happen an SQLAlchemy exception should be raised
        # making the test fail
        data = {**user_data, **restaurant_data}
        with app.test_request_context():
            operator_form = OperatorForm(**data)
            user_form = UserForm(**user_data)
            user_form.email.data = "test2@test.com"
            operator = new_operator(operator_form, __submit=False)
            user = new_user(user_form, __submit=False, __password="pass")
            add_review(operator.id, operator.restaurant_id, 3)
            add_review(user.id, operator.restaurant_id, 3, text="Test")
            update_review(operator.restaurant, 4)
            

if __name__ == '__main__':
    unittest.main()
