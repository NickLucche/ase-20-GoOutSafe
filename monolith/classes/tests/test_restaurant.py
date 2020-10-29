from monolith.classes.exceptions import FormValidationError
from monolith.classes.user import new_operator
from monolith.forms import OperatorForm, RestaurantProfileEditForm
from monolith.classes.tests.utils import *
import unittest
from monolith.classes.restaurant import edit_tables


class TestRestaurant(unittest.TestCase):
    
    def test_edit(self):
        app = setup_for_test()

        data = {**user_data, **restaurant_data}
        request = {'table_1' : 4,
                  'table_2' : 7,
                  'table_3' : 11}
        with app.test_request_context():
            operator_form = OperatorForm(**data)
            edit_form = RestaurantProfileEditForm(**data)
            operator = new_operator(operator_form, __submit=False)
            edit_tables(edit_form, request, operator.restaurant_id, __submit=False)
            try:
                edit_tables(edit_form, request, operator.restaurant_id)
                return False
            except FormValidationError:
                return True


if __name__ == '__main__':
    unittest.main()
