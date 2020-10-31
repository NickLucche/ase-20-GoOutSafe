from monolith.classes import restaurant
from monolith.database import Restaurant, db, User, Reservation
from datetime import datetime, timedelta, time
import random
from flask import Flask

def add_random_users(n_users: int, app: Flask):
    with app.app_context():
        for i in range(n_users):
            user = User(email='test', firstname=f'test_{i}', lastname=f'test_{i}', 
            password='test', dateofbirth=datetime.now(), is_active=bool(random.randrange(0, 2)),
            is_admin=False)
            # print(f"Adding user {user}")
            db.session.add(user)
            db.session.commit()

def delete_random_users(app: Flask):
    with app.app_context():
        delete_query = User.__table__.delete().where(User.email == 'test')
        db.session.execute(delete_query)
        db.session.commit()

def add_random_restaurants(n_places: int, app: Flask):
    with app.app_context():
        rests = []
        for i in range(n_places):
            stay_time = time(hour=1)
            res = Restaurant(name=f'test_rest_{i}', likes = 10, lat = 42.111,lon = 11.111, phone = '343493490',
             extra_info = '', avg_stay_time=stay_time)
            rests.append(res)
        db.session.add_all(rests)
        db.session.commit()
    

def random_datetime_in_range(start, end):
    # from https://stackoverflow.com/questions/553303/generate-a-random-date-between-two-other-dates#answer-553448
    if start == end:
        return start
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = random.randrange(int_delta)
    return start + timedelta(seconds=random_second)

def mark_random_guy_as_positive(app: Flask, positive_date: datetime):
    with app.app_context():
        rand_row = random.randrange(2, db.session.query(User).count()) 
        positive_guy = db.session.query(User)[rand_row]
        print(f"Marking user {positive_guy} as positive to COVID-19")
        positive_guy.is_positive = True
        positive_guy.confirmed_positive_date = positive_date
        db.session.commit()
        return positive_guy.to_dict()

def visit_random_places(app: Flask, pos_id:int, positive_date: datetime, time_span: int, n_places: int, time_span_offset:int=5):
    # return visits to places within time_span days
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
            
            visit_date = random_datetime_in_range(positive_date-timedelta(days=time_span+time_span_offset), positive_date)
            visit = Reservation(user_id=pos_id, 
            restaurant_id=rid, reservation_time=visit_date, 
            table_no=0, seats=1, entrance_time=visit_date)
            if visit_date >= risky_date:
                visits.append(visit)
                risky_places += 1
        db.session.add_all(visits)
        db.session.commit()
        return risky_places, [v.to_dict() for v in visits]

def add_random_visits_to_place(app: Flask, restaurant_id:int, start_date: datetime, end_date: datetime, pos_date:datetime, min_visits:int=0, max_visits:int=5):
    visits = []
    n_visits = random.randint(min_visits, max_visits)
    risky_visits = 0
    with app.app_context():
        # make a bunch of reservations
        for _ in range(n_visits):
            # some random id identifying a user
            rand_user = random.randint(1000, 2000)
            visit_date = random_datetime_in_range(start_date, end_date)
            # compute 'danger period' in which user might have been in contact with positive dude
            stay_time = Restaurant.query.filter_by(id=restaurant_id).first().avg_stay_time
            staying_interval = timedelta(hours=stay_time.hour, minutes=stay_time.minute, seconds=stay_time.second)
            if visit_date <= (pos_date + staying_interval) and visit_date >= (pos_date - staying_interval) :
                print("RISKY VISIT:", visit_date, pos_date, rand_user, restaurant_id)
                risky_visits += 1
            visit = Reservation(user_id=rand_user, 
            restaurant_id=restaurant_id, reservation_time=visit_date, 
            table_no=0, seats=1, entrance_time=visit_date)
            visits.append(visit)
        db.session.add_all(visits)
        db.session.commit()
        return risky_visits