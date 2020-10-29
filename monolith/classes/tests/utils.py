from monolith.classes import restaurant
from monolith.database import db, User, Reservation
from datetime import datetime, timedelta
import random
from flask import Flask


def add_random_users(n_users: int, app: Flask):
    with app.app_context():
        for i in range(n_users):
            user = User(email='test',
                        firstname=f'test_{i}',
                        lastname=f'test_{i}',
                        password='test',
                        dateofbirth=datetime.now(),
                        is_active=bool(random.randrange(0, 2)),
                        is_admin=False)
            print(f"Adding user {user}")
            db.session.add(user)
            db.session.commit()


def delete_random_users(app: Flask):
    with app.app_context():
        delete_query = User.__table__.delete().where(User.email == 'test')
        db.session.execute(delete_query)
        db.session.commit()


def random_datetime_in_range(start, end):
    # from https://stackoverflow.com/questions/553303/generate-a-random-date-between-two-other-dates#answer-553448
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = random.randrange(int_delta)
    return start + timedelta(seconds=random_second)


def add_random_restaurant(n_restaurants: int, app: Flask):
    with app.app_context():
        for i in range(n_restaurants):
            restaurant = Restaurant(name=f'test_{i}',
                        likes=0,
                        lat=0,
                        lon=0,
                        phone=-1,
                        extra_info='')
            print(f"Adding restaurant {restaurant}")
            db.session.add(restaurant)
            db.session.commit()

def add_random_reservation(user):
    with app.app_context():
        for i in range(n_users):
            user = User(email='test',
                        firstname=f'test_{i}',
                        lastname=f'test_{i}',
                        password='test',
                        dateofbirth=datetime.now(),
                        is_active=bool(random.randrange(0, 2)),
                        is_admin=False)
            print(f"Adding user {user}")
            db.session.add(user)
            db.session.commit()
def mark_random_guy_as_positive(app: Flask, positive_date: datetime):
    with app.app_context():
        rand_row = random.randrange(2, db.session.query(User).count()) 
        positive_guy = db.session.query(User)[rand_row]
        print(f"Marking user {positive_guy} as positive to COVID-19")
        positive_guy.is_positive = True
        positive_guy.confirmed_positive_date = positive_date
        db.session.commit()
        return positive_guy.to_dict()

def visit_random_places(app: Flask, pos_id:int, positive_date: datetime, time_span: int, n_places: int):
    visits = []
    visited_places = []
    risky_places = 0
    with app.app_context():
        risky_date = positive_date - timedelta(days=time_span)
        risky_date.replace(hour=0, minute=0, second=0, microsecond=0)
        # make a bunch of reservations
        for _ in range(n_places):
            # visit a random restaurant not seen before
            rid = random.randint(0, n_places*10)
            while rid in visited_places: 
                rid = random.randint(0, n_places*10)
            visited_places.append(rid)
            
            visit_date = random_datetime_in_range(positive_date-timedelta(days=time_span+5), positive_date)
            visit = Reservation(user_id=pos_id, 
            restaurant_id=rid, reservation_time=visit_date, 
            table_no=0, turn=0, seats=1, entrance_time=visit_date)
            visits.append(visit)
            if visit_date >= risky_date:
                risky_places += 1
        db.session.add_all(visits)
        db.session.commit()
        return risky_places, [v.to_dict() for v in visits]

def add_random_visits_to_place(app: Flask, restaurant_id:int, start_date: datetime, end_date: datetime, pos_date:datetime):
    visits = []
    n_visits = random.randint(0, 5)
    risky_visits = 0
    with app.app_context():
        # make a bunch of reservations
        for _ in range(n_visits):
            # some random id identifying a user
            rand_user = random.randint(1000, 2000)
            visit_date = random_datetime_in_range(start_date, end_date)
            if visit_date.date() == pos_date.date():
                print("RISKY VISIT:", visit_date, pos_date)
                risky_visits += 1
            visit = Reservation(user_id=rand_user, 
            restaurant_id=restaurant_id, reservation_time=visit_date, 
            table_no=0, seats=1, entrance_time=visit_date, turn=0)
            visits.append(visit)
        db.session.add_all(visits)
        db.session.commit()
        return risky_visits
