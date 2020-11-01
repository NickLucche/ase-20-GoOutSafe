import unittest
from monolith.database import Notification, Reservation, Restaurant, db, User
import random
from datetime import datetime, timedelta
from monolith.classes.notifications import check_visited_places, create_notifications, contact_tracing, fetch_operator_notifications
from monolith.app import create_app
from monolith.classes.tests.utils import add_random_users, add_random_visits_to_place, delete_random_users, mark_random_guy_as_positive, random_datetime_in_range, visit_random_places, add_random_restaurants
from celery import chain

app = create_app()
INCUBATION_PERIOD_COVID= 14
class Notifications(unittest.TestCase):

    def setUp(self):
        # executed before executing each test
        self.now = datetime.now()
        add_random_users(10, app)
        add_random_restaurants(10*10*10, app)
        # LHA marks a User as positive (admin excluded)
        positive_guy = mark_random_guy_as_positive(app, self.now)

    def tearDown(self):
        with app.app_context():
            # executed after each test, regardless of outcome
            delete_random_users(app)
            # delete all reservations
            db.session.query(Reservation).delete()
            db.session.query(Notification).delete()
            db.session.query(Restaurant).delete()
            db.session.commit()
        

    def test_lha_positive_marking(self):
        with app.app_context():
            poor_guy = User.query.filter_by(is_positive=True).first()
        self.assertEqual(poor_guy.confirmed_positive_date, self.now.date())
        self.assertNotEqual(poor_guy.id, 1)

    def test_user_visited_places_sync(self):
        with app.app_context():
            positive_guy = User.query.filter_by(is_positive=True).first().to_dict()
            
            # make it so that user visited a random number of places
            n_places = random.randrange(0, 10)
            nrisky_places, visits = visit_random_places(app, positive_guy['id'], self.now, INCUBATION_PERIOD_COVID, n_places)
            # get restaurants visited by positive user in the last `INCUBATION_PERIOD_COVID` days
            reservations = check_visited_places(positive_guy['id'], INCUBATION_PERIOD_COVID)
        # check every positive user visit was correctly retrieved
        self.assertEqual(len(reservations), nrisky_places)
        self.assertDictEqual({v['id']:v for v in visits}, {r['id']: r for r in reservations})
        
    # here we need to have celery workers processes up and running
    def test_user_visited_places_async(self):
        with app.app_context():
            positive_guy = User.query.filter_by(is_positive=True).first().to_dict()
            
            # make it so that user visited a random number of places
            n_places = random.randrange(0, 10)
            nrisky_places, visits = visit_random_places(app, positive_guy['id'], self.now, INCUBATION_PERIOD_COVID, n_places)
            # get restaurants visited by positive user in the last `INCUBATION_PERIOD_COVID` days
            # this forces a wait
            reservations = check_visited_places.delay(positive_guy['id'], INCUBATION_PERIOD_COVID).get()
            # print(reservations)

         # check every positive user visit was correctly retrieved
        self.assertEqual(len(reservations), nrisky_places)
        # json conversion happened
        # self.assertDictEqual({v['id']:v for v in visits}, {r['id']: r for r in reservations})

    def test_contact_tracing(self):
        with app.app_context():
            positive_guy = User.query.filter_by(is_positive=True).first().to_dict()

            # make positive guy visit some random places
            n_places = random.randrange(0, 10)
            nrisky_places, visits = visit_random_places(app, positive_guy['id'], self.now, INCUBATION_PERIOD_COVID, n_places)
            # have a random num of users visit the same place as the positive guy
            print("PLACES VISITED BY POSITIVE:", visits)
            nrisky_visits = 0
            for v in visits:
                nrisky_visits += add_random_visits_to_place(app, v['restaurant_id'],
                 self.now-timedelta(days=INCUBATION_PERIOD_COVID), self.now, v['entrance_time'])
                    
            # check if positive guy visited any restaurant in the last `INCUBATION_PERIOD_COVID` days
            reservations = check_visited_places(positive_guy['id'], INCUBATION_PERIOD_COVID)
            # notify customers that have been to the same restaurants at the same time as the pos guy
            notified_users = contact_tracing(reservations, positive_guy['id'])
            print("Notified users", notified_users)

        self.assertEqual(len(notified_users), nrisky_visits)

    def test_contact_tracing_async(self):
        with app.app_context():
            positive_guy = User.query.filter_by(is_positive=True).first().to_dict()

            # make positive guy visit some random places
            n_places = random.randrange(0, 10)
            nrisky_places, visits = visit_random_places(app, positive_guy['id'], self.now, INCUBATION_PERIOD_COVID, n_places)
            # have a random num of users visit the same place as the positive guy
            print("PLACES VISITED BY POSITIVE:", visits)
            nrisky_visits = 0
            for v in visits:
                nrisky_visits += add_random_visits_to_place(app, v['restaurant_id'],
                 self.now-timedelta(days=INCUBATION_PERIOD_COVID), self.now, v['entrance_time'])
                    
            # run async task enforcing chain execution using signatures
            pos_id = positive_guy['id']
            exec_chain = (check_visited_places.s(pos_id, INCUBATION_PERIOD_COVID) | contact_tracing.s(pos_id))()
            
            to_be_notified_users = exec_chain.get()
            print("Notified users", to_be_notified_users)

        self.assertEqual(len(to_be_notified_users), nrisky_visits)

    def test_operator_notifications(self):
        with app.app_context():
            positive_guy = User.query.filter_by(is_positive=True).first().to_dict()

            # generate positive user visits to random restaurants in last 14 days
            n_places = random.randrange(1, 10)
            nrisky_places, risky_visits = visit_random_places(app, positive_guy['id'], self.now,\
                 INCUBATION_PERIOD_COVID, n_places, time_span_offset=0)
            print(f"User {positive_guy['id']} visited {nrisky_places} restaurants")
            # generate other users visits to same restaurants in same days
            visits_per_rest = {}
            for visit in risky_visits:
                rid = visit['restaurant_id']
                et = visit['entrance_time']
                visits_per_rest[rid] = add_random_visits_to_place(app, rid, et, et, et, min_visits=1, max_visits=3)
                print(f"Some other {visits_per_rest[rid]} users visited restaurant {rid}")
            # execute pipeline async to generate notifications
            # run async tasks: check visited places -> check customers in danger -> write notifications
            pos_id = positive_guy['id']
            exec_chain = (check_visited_places.s(pos_id, INCUBATION_PERIOD_COVID) |
             contact_tracing.s(pos_id) | create_notifications.s(pos_id))()
            
            notifs = exec_chain.get()
            db_notifications = [n.to_dict() for n in Notification.query.filter_by(user_notification=False).all()]
            print("Operator Notifications in db:", db_notifications)
            print("Notifications written:", notifs)
            # make sure every operator got their notification
            for v in risky_visits:
                rid = v['restaurant_id']
                et = v['entrance_time']
                rnot = fetch_operator_notifications(app, rid)
                print(f"[{rid}] REST NOTIFICATION:", rnot)
                self.assertEqual(len(rnot), 1)
                self.assertEqual(rnot[0]['date'], et)

        self.assertEqual(len(db_notifications), nrisky_places)


    def test_user_notifications(self):
        with app.app_context():
            positive_guy = mark_random_guy_as_positive(app, self.now)
            # generate positive user visits to random restaurants in last 14 days
            n_places = random.randrange(1, 10)
            nrisky_places, risky_visits = visit_random_places(app, positive_guy['id'], self.now, INCUBATION_PERIOD_COVID, n_places, time_span_offset=0)
            print(f"User {positive_guy['id']} visited {nrisky_places} restaurants")
            # generate other users visits to same restaurants in same days
            visits_per_rest = {}
            for visit in risky_visits:
                rid = visit['restaurant_id']
                et = visit['entrance_time']
                visits_per_rest[rid] = add_random_visits_to_place(app, rid, et, et, et, min_visits=1, max_visits=3)
                print(f"Some other {visits_per_rest[rid]} users visited restaurant {rid}")
            # execute pipeline async to generate notifications
            # run async tasks: check visited places -> check customers in danger -> write notifications
            pos_id = positive_guy['id']
            exec_chain = (check_visited_places.s(pos_id, INCUBATION_PERIOD_COVID) |
             contact_tracing.s(pos_id) | create_notifications.s(pos_id))()
            
            notifs = exec_chain.get()
            db_notifications = [n.to_dict() for n in Notification.query.filter_by(user_notification=True).all()]
            print("User Notifications in db:", db_notifications)
            # print("Notifications written:", notifs)

        # check that every user had their notifications generated
        self.assertEqual(len(db_notifications), sum(visits_per_rest.values()))