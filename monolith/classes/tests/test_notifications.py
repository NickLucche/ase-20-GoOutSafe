import unittest
from monolith.database import db, User
import random
from datetime import datetime
from monolith.classes.notifications import check_visited_places

class Notifications(unittest.TestCase):

    def test_positive_visited_my_restaurant():
        # as operator, I want to be notified if a positive customer visited my restaurant
        # within the last X days  

        # LHA marks a User as positive
        rand_row = random.randrange(0, db.session.query(User).count()) 
        positive_guy = db.session.query(User)[rand_row]

        positive_guy.is_positive = True
        positive_guy.confirmed_positive_date = datetime.now()
        db.session.commit()

        # Shortcut to send a task message
        check_visited_places.delay(positive_guy)
 
