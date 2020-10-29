from monolith.database import db, User
from monolith.views import blueprints
from monolith.auth import login_manager
import datetime
from datetime import timedelta
import random
from flask import Flask

user_data = {'email':'prova@prova.com', 
        'firstname':'Mario', 
        'lastname':'Rossi', 
        'dateofbirth': datetime.datetime(1960, 12, 3)}

clear_password = 'pass'

restaurant_data = {'name': 'Mensa martiri', 
                    'lat': '4.12345',
                    'lon': '5.67890',
                    'phone': '3333333333',
                    'extra_info': 'Rigatoni dorati h24, cucina povera'}

def test_setup():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['WTF_CSRF_SECRET_KEY'] = 'A SECRET KEY'
    app.config['SECRET_KEY'] = 'ANOTHER ONE'

    for bp in blueprints:
        app.register_blueprint(bp)
        bp.app = app

    db.init_app(app)
    login_manager.init_app(app)
    db.create_all(app=app)
    return app

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