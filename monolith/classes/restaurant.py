
from monolith.forms import RestaurantProfileEditForm
from monolith.classes.exceptions import FormValidationError
from monolith.database import RestaurantTable, Review, db


def edit_restaurant(form:RestaurantProfileEditForm, request_form, restaurant_id : int, __submit=True):
    """Updates the profile and the tables of a restaurant. Note: all the tables must be passed with
    the request, not just the new ones.

    Args:
        form ([RestaurantProfileEditForm]): the editing form
        request_form: the table editing request
        restaurant_id (int): the restaurant id
        __submit (bool, optional): False to not to perform the submit validation (only for tests!). Defaults to True.

    Raises:
        FormValidationError: [if the form is not well formed]
    """
    validate = form.validate_on_submit() if __submit else True
    if validate:
        RestaurantTable.query.filter_by(restaurant_id = restaurant_id).delete()
        db.session.commit()
        i = 1
        while request_form.get('table_' + str(i)) != None:
            new_table = RestaurantTable()
            new_table.restaurant_id = int(restaurant_id)
            new_table.table_id = int(i)
            new_table.seats = int(request_form.get('table_' + str(i)))
            db.session.add(new_table)
            i += 1
        db.session.commit()
    else:
        raise FormValidationError()

def add_review(user_id, restaurant_id, stars, text=None):
    """Add a new review for the restaurant.

    Args:
        user_id (int): the reviewer id
        restaurant_id (int): the restaurant id
        stars (int): the number of stars
        text (string, optional): The text review, if any. Defaults to None.
    """
    if text:
        r = Review(reviewer_id=user_id, restaurant_id=restaurant_id, stars=stars, text_review=text)
    else:
        r = Review(reviewer_id=user_id, restaurant_id=restaurant_id, stars=stars)
    
    db.session.add(r)
    db.session.commit()

def update_review(restaurant, stars_no):
    # updates restaurant view with newly written review so that user can see its change immediately
    restaurant.num_reviews += 1
    restaurant.avg_stars = 1/restaurant.num_reviews * \
        (restaurant.avg_stars * (restaurant.num_reviews-1) + stars_no)
    return restaurant

