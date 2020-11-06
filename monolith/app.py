import os
from flask import Flask
from monolith.database import db, User, Restaurant, Reservation, RestaurantTable
from monolith.views import blueprints
from monolith.auth import login_manager
import datetime
from datetime import time

def create_app(dbfile='sqlite:///gooutsafe.db'):
    app = Flask(__name__)
    app.config['WTF_CSRF_SECRET_KEY'] = 'A SECRET KEY'
    app.config['SECRET_KEY'] = 'ANOTHER ONE'
    app.config['SQLALCHEMY_DATABASE_URI'] = dbfile
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # celery config
    app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379'
    app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379'

    for bp in blueprints:
        app.register_blueprint(bp)
        bp.app = app

    db.init_app(app)
    login_manager.init_app(app)
    #db.drop_all(app=app)
    db.create_all(app=app)

    # create a first admin user
    with app.app_context():
        q = db.session.query(User).filter(User.email == 'authority@authority.com')
        user = q.first()
        if user is None:
            example = User()
            example.firstname = 'Authority'
            example.lastname = 'Authority'
            example.email = 'authority@authority.com'
            example.phone = '3334567890'
            example.fiscal_code = 'SURNAM95A32B123C'
            example.dateofbirth = datetime.datetime(2020, 10, 5)
            example.is_admin = True
            example.set_password('authority')
            example.is_positive = False
            db.session.add(example)
            db.session.commit()

        q = db.session.query(User).filter(User.email == 'example@example.com')
        user = q.first()
        if user is None:
            example = User()
            example.firstname = 'Admin'
            example.lastname = 'Admin'
            example.email = 'example@example.com'
            example.phone = '3334567891'
            example.fiscal_code = 'SURNAM95A32B123D'
            example.dateofbirth = datetime.datetime(2020, 10, 5)
            example.is_admin = True
            example.set_password('admin')
            example.is_positive = False
            db.session.add(example)
            db.session.commit()

        q = db.session.query(User).filter(User.email == 'user1@example.com')
        user = q.first()
        if user is None:
            example = User()
            example.firstname = 'User1'
            example.lastname = 'User1'
            example.email = 'user1@example.com'
            example.phone = '3334567893'
            example.fiscal_code = 'SURNAM95A32B123E'
            example.dateofbirth = datetime.datetime(2020, 10, 5)
            example.is_admin = False
            example.set_password('user1')
            example.is_positive = False
            db.session.add(example)
            db.session.commit()

        q = db.session.query(User).filter(User.email == 'user2@example.com')
        user = q.first()
        if user is None:
            example = User()
            example.firstname = 'User2'
            example.lastname = 'User2'
            example.email = 'user2@example.com'
            example.phone = '3334567894'
            example.fiscal_code = 'SURNAM95A32B123F'
            example.dateofbirth = datetime.datetime(2020, 10, 5)
            example.is_admin = False
            example.set_password('user2')
            example.is_positive = False
            db.session.add(example)
            db.session.commit()

        q = db.session.query(Restaurant).filter(Restaurant.id == 1)
        restaurant = q.first()
        if restaurant is None:
            restaurant = Restaurant()
            restaurant.name = 'Trial Restaurant'
            restaurant.avg_stay_time = time(hour=1)
            restaurant.likes = 42
            restaurant.phone = '555123456'
            restaurant.lat = 43.720586
            restaurant.lon = 10.408347
            restaurant.avg_stay_time = datetime.time(1, 30)
            db.session.add(restaurant)
            db.session.commit()
        
        q = db.session.query(User).filter(User.restaurant_id != None)
        operator = q.first()
        if operator is None:
            operator = User(firstname="Operator", lastname="Operator", email="operator@example.com", restaurant=restaurant, dateofbirth=datetime.datetime(2020, 10, 29))
            #operator.restaurant_id = restaurant.id
            operator.set_password("operator")
            db.session.add(operator)
            db.session.commit()

        q = db.session.query(RestaurantTable).filter(RestaurantTable.restaurant == restaurant)
        restaurant_table = q.first()
        if restaurant_table is None:
            restaurant_table = RestaurantTable(table_id=1, restaurant=restaurant, seats=4)
            db.session.add(restaurant_table)
            db.session.commit()

        q = db.session.query(Reservation).filter(Reservation.restaurant == restaurant);
        reservation = q.first()
        if reservation is None:
            now = datetime.datetime.now()
            reservation1 = Reservation(entrance_time = now - datetime.timedelta(days=1), table=restaurant_table, restaurant=restaurant, user_id=3, seats=3)
            reservation2 = Reservation(entrance_time = now - datetime.timedelta(days=1), table=restaurant_table, restaurant=restaurant, user_id=4, seats=3)
            db.session.add(reservation1)
            db.session.add(reservation2)
            db.session.commit()

    return app


if __name__ == '__main__':
    app = create_app()
    app.run()
