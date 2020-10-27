from monolith.database import db, User
from datetime import datetime, timedelta
import random
from flask import Flask

def add_random_users(n_users: int, app: Flask):
    with app.app_context():
        for i in range(n_users):
            user = User(email='test', firstname=f'test_{i}', lastname=f'test_{i}', 
            password='test', dateofbirth=datetime.now(), is_active=bool(random.randrange(0, 2)),
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