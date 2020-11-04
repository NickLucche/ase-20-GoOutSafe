from monolith.classes.ratings_task import average_review_stars
from monolith.classes.tests.utils import *
from monolith.database import db, User, Review, Restaurant
import unittest
import random

class TestRatings(unittest.TestCase):

    def setUp(self):
        self.app = setup_for_test()
        add_random_users(1, self.app)
        add_random_restaurants(1, self.app)

    def tearDown(self):
        delete_random_users(self.app)
        with self.app.app_context():
            db.session.query(Reservation).delete()
            db.session.query(Review).delete()

    def test_single_review_update(self):
        # user makes a review
        with self.app.app_context():
            stars = random.randint(1, 5)
            reviewer = User.query.filter_by(email='test').first()
            rest = Restaurant.query.filter_by(name='test_rest_0').first().to_dict()
            review = Review(reviewer_id=reviewer.id, stars=stars, restaurant_id=rest['id'])
            db.session.add(review)
            db.session.commit()
            # compute mean
            average_review_stars()
            # makes sure it checks out
            rest = Restaurant.query.filter_by(id=rest['id']).first()
            self.assertEqual(rest.avg_stars, stars)
            self.assertEqual(rest.num_reviews, 1)
            
