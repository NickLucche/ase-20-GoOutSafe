
from monolith.classes.exceptions import FormValidationError
from monolith.database import RestaurantTable, Review, db


def edit_tables(form, request_form, restaurant_id : int, __submit=True):
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
    if text:
        r = Review(reviewer_id=user_id, restaurant_id=restaurant_id, stars=stars, text_review=text)
    else:
        r = Review(reviewer_id=user_id, restaurant_id=restaurant_id, stars=stars)
    
    db.session.add(r)
    db.session.commit()

def update_review(restaurant, stars_no):
    # updates restaurant view with newly written review
    restaurant.num_reviews += 1
    restaurant.avg_stars = 1/restaurant.num_reviews * \
        (restaurant.avg_stars * (restaurant.num_reviews-1) + stars_no)
    return restaurant

