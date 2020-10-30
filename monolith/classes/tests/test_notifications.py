import unittest
from monolith.database import Notification, Reservation, db, User
import random
from datetime import datetime, timedelta
from monolith.classes.notifications import check_visited_places, create_notifications, contact_tracing, fetch_operator_notifications
from monolith.app import create_app
from monolith.classes.tests.utils import add_random_users, add_random_visits_to_place, delete_random_users, mark_random_guy_as_positive, random_datetime_in_range, visit_random_places
from celery import chain

app = create_app()
INCUBATION_PERIOD_COVID= 14
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

    def test_user_visited_places_sync(self):
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
            reservations = check_visited_places(positive_guy.id, INCUBATION_PERIOD_COVID)
            # delete all reservations
            db.session.query(Reservation).delete()
            db.session.commit()

        delete_random_users(app)
        self.assertEqual(len(reservations), risky_places)
        
    # here we need to have celery workers processes up and running
    def test_user_visited_places_async(self):
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
            for _ in range(n_places):
                visit_date = random_datetime_in_range(now-timedelta(days=INCUBATION_PERIOD_COVID+5), now)
                visit = Reservation(user_id=positive_guy.id, 
                restaurant_id=random.randint(0, 10), reservation_time=visit_date, 
                table_no=0, seats=1, entrance_time=visit_date)
                visits.append(visit)
                if visit_date >= risky_date:
                    risky_places += 1
            db.session.add_all(visits)
            db.session.commit()
            # this forces a wait
            reservations = check_visited_places.delay(positive_guy.id, INCUBATION_PERIOD_COVID).get()
            print(reservations)
            # delete all reservations
            db.session.query(Reservation).delete()
            db.session.commit()

        delete_random_users(app)
        self.assertEqual(len(reservations), risky_places)

    def test_contact_tracing(self):
        add_random_users(10, app)
        now = datetime.now()
        # LHA marks a User as positive (admin excluded)
        with app.app_context():
            positive_guy = mark_random_guy_as_positive(app, now)
            # make positive guy visit some random places
            n_places = random.randrange(0, 10)
            nrisky_places, visits = visit_random_places(app, positive_guy['id'], now, INCUBATION_PERIOD_COVID, n_places)
            # have a random num of users visit the same place as the positive guy
            print("PLACES VISITED BY POSITIVE:", visits)
            nrisky_visits = 0
            for v in visits:
                nrisky_visits += add_random_visits_to_place(app, v['restaurant_id'],
                 now-timedelta(days=INCUBATION_PERIOD_COVID), now, v['entrance_time'])
                    
            # check if positive guy visited any restaurant in the last `INCUBATION_PERIOD_COVID` days
            reservations = check_visited_places(positive_guy['id'], INCUBATION_PERIOD_COVID)
            # notify customers that have been to the same restaurants at the same time as the pos guy
            notified_users = contact_tracing(reservations, positive_guy['id'])
            print("Notified users", notified_users)
            # delete all reservations
            db.session.query(Reservation).delete()
            db.session.commit()

        delete_random_users(app)
        self.assertEqual(len(notified_users), nrisky_visits)

    def test_contact_tracing_async(self):
        add_random_users(10, app)
        now = datetime.now()
        # LHA marks a User as positive (admin excluded)
        with app.app_context():
            positive_guy = mark_random_guy_as_positive(app, now)
            # make positive guy visit some random places
            n_places = random.randrange(0, 10)
            nrisky_places, visits = visit_random_places(app, positive_guy['id'], now, INCUBATION_PERIOD_COVID, n_places)
            # have a random num of users visit the same place as the positive guy
            print("PLACES VISITED BY POSITIVE:", visits)
            nrisky_visits = 0
            for v in visits:
                nrisky_visits += add_random_visits_to_place(app, v['restaurant_id'],
                 now-timedelta(days=INCUBATION_PERIOD_COVID), now, v['entrance_time'])
                    
            # run async task enforcing chain execution using signatures
            pos_id = positive_guy['id']
            exec_chain = (check_visited_places.s(pos_id, INCUBATION_PERIOD_COVID) | contact_tracing.s(pos_id))()
            
            to_be_notified_users = exec_chain.get()
            print("Notified users", to_be_notified_users)
            # delete all reservations
            db.session.query(Reservation).delete()
            db.session.commit()

        delete_random_users(app)
        self.assertEqual(len(to_be_notified_users), nrisky_visits)

    def test_operator_notifications(self):
        add_random_users(10, app)
        now = datetime.now()
        # LHA marks a User as positive (admin excluded)
        with app.app_context():
            positive_guy = mark_random_guy_as_positive(app, now)
            # generate positive user visits to random restaurants in last 14 days
            n_places = random.randrange(1, 10)
            nrisky_places, risky_visits = visit_random_places(app, positive_guy['id'], now, INCUBATION_PERIOD_COVID, n_places, time_span_offset=0)
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

            # delete all reservations
            db.session.query(Reservation).delete()
            # and notifications
            db.session.query(Notification).delete()
            db.session.commit()

        delete_random_users(app)

        self.assertEqual(len(db_notifications), nrisky_places)


    def test_user_notifications(self):
        add_random_users(10, app)
        now = datetime.now()
        # LHA marks a User as positive (admin excluded)
        with app.app_context():
            positive_guy = mark_random_guy_as_positive(app, now)
            # generate positive user visits to random restaurants in last 14 days
            n_places = random.randrange(1, 10)
            nrisky_places, risky_visits = visit_random_places(app, positive_guy['id'], now, INCUBATION_PERIOD_COVID, n_places, time_span_offset=0)
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

            # delete all reservations
            db.session.query(Reservation).delete()
            # and notifications
            db.session.query(Notification).delete()
            db.session.commit()

        delete_random_users(app)
        # check that every user had their notifications generated
        self.assertEqual(len(db_notifications), sum(visits_per_rest.values()))