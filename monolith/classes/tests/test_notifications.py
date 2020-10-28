import unittest
from monolith.database import Reservation, db, User
import random
from datetime import datetime, timedelta
from monolith.classes.notifications import check_visited_places
from monolith.app import create_app
from monolith.classes.tests.utils import add_random_users, delete_random_users, random_datetime_in_range

app = create_app()
INCUBATION_PERIOD_COVID= 10

class Notifications(unittest.TestCase):
    def test_lha_positive_marking(self):
        add_random_users(10, app)
        now = datetime.now()
        # LHA marks a User as positive (admin excluded)
        with app.app_context():
            rand_row = random.randrange(1, db.session.query(User).count())
            positive_guy = db.session.query(User)[rand_row]
            print(f"Marking user {positive_guy} as positive to COVID-19")
            positive_guy.is_positive = True
            positive_guy.confirmed_positive_date = now
            db.session.commit()

            poor_guy = User.query.filter_by(id=positive_guy.id).first()
        delete_random_users(app)
        self.assertEqual(poor_guy.is_positive, True)
        self.assertEqual(poor_guy.confirmed_positive_date, now)
        self.assertEqual(positive_guy.id, poor_guy.id)

    def test_user_visited_places(self):
        add_random_users(10, app)
        now = datetime.now()
        # LHA marks a User as positive (admin excluded)
        with app.app_context():
            rand_row = random.randrange(1, db.session.query(User).count()) 
            positive_guy = db.session.query(User)[rand_row]
            print(f"Marking user {positive_guy} as positive to COVID-19")
            positive_guy.is_positive = True
            positive_guy.confirmed_positive_date = now
            db.session.commit()
            # make it so that user visited a random number of places
            n_places = random.randrange(0, 10)
            visits = []
            risky_places = 0
            risky_date = now - timedelta(days=INCUBATION_PERIOD_COVID)
            risky_date.replace(hour=0, minute=0, second=0, microsecond=0)
            for i in range(n_places):
                visit_date = random_datetime_in_range(now-timedelta(days=INCUBATION_PERIOD_COVID+5), now)
                visit = Reservation(user_id=positive_guy.id, 
                restaurant_id=random.randint(0, 10), reservation_time=visit_date, 
                table_no=0, seats=1, entrance_time=visit_date)
                visits.append(visit)
                if visit_date >= risky_date:
                    risky_places += 1
            db.session.add_all(visits)
            db.session.commit()
            reservations = check_visited_places(positive_guy, 10, app)
            # delete all reservations
            db.session.query(Reservation).delete()
            db.session.commit()

        delete_random_users(app)
        self.assertEqual(len(reservations), risky_places)


    # def test_user_visited_places_celery(self):
    #     add_random_users(10, app)
    #     now = datetime.now()
    #     # LHA marks a User as positive (admin excluded)
    #     with app.app_context():
    #         rand_row = random.randrange(1, db.session.query(User).count())
    #         positive_guy = db.session.query(User)[rand_row]
    #         print(f"Marking user {positive_guy} as positive to COVID-19")
    #         positive_guy.is_positive = True
    #         positive_guy.confirmed_positive_date = now
    #         db.session.commit()

    #     check_visited_places.delay()
    #     delete_random_users(app)
    #     self.assertEqual(poor_guy.is_positive, True)
    #     self.assertEqual(poor_guy.confirmed_positive_date, now)
    #     self.assertEqual(positive_guy.id, poor_guy.id)

    # def test_positive_visited_my_restaurant(self):
    #     # as operator, I want to be notified if a positive customer visited my restaurant
    #     # within the last X days
    #     add_random_users(10, app)

    #     # LHA marks a User as positive (admin excluded)
    #     rand_row = random.randrange(1, db.session.query(User).count())
    #     positive_guy = db.session.query(User)[rand_row]
    #     print(f"Marking user {positive_guy} as positive to COVID-19")
    #     positive_guy.is_positive = True
    #     positive_guy.confirmed_positive_date = datetime.now()
    #     db.session.commit()

    #     # Shortcut to send a task message
    #     # check_visited_places.delay(positive_guy)

    #     delete_random_users(app)
