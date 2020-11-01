import os
from flask import Flask
from monolith.database import db, User, Restaurant, Reservation, RestaurantTable
from monolith.views import blueprints
from monolith.auth import login_manager
import datetime

def create_app():
    app = Flask(__name__)
    app.config['WTF_CSRF_SECRET_KEY'] = 'A SECRET KEY'
    app.config['SECRET_KEY'] = 'ANOTHER ONE'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gooutsafe.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # celery config
    app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379'
    app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379'

    for bp in blueprints:
        app.register_blueprint(bp)
        bp.app = app

    db.init_app(app)
    login_manager.init_app(app)
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
            example.phone_number = '3334567890'
            example.ssn = 'SURNAM95A32B123C'
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
            example.phone_number = '3334567891'
            example.ssn = 'SURNAM95A32B123D'
            example.dateofbirth = datetime.datetime(2020, 10, 5)
            example.is_admin = True
            example.set_password('admin')
            example.is_positive = False
            db.session.add(example)
            db.session.commit()

        q = db.session.query(Restaurant).filter(Restaurant.id == 1)
        restaurant = q.first()
        if restaurant is None:
            restaurant = Restaurant()
            restaurant.name = 'Trial Restaurant'
            restaurant.likes = 42
            restaurant.phone = 555123456
            restaurant.lat = 43.720586
            restaurant.lon = 10.408347
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
            restaurant_table = RestaurantTable(restaurant=restaurant, seats=4)
            db.session.add(restaurant_table)
            db.session.commit()

        q = db.session.query(Reservation).filter(Reservation.restaurant == restaurant);
        reservation = q.first()
        if reservation is None:
            now = datetime.datetime.now()
            reservation1 = Reservation(entrance_time = now - datetime.timedelta(days=1), table=restaurant_table, restaurant=restaurant, user_id=1, seats=3)
            reservation2 = Reservation(entrance_time = now - datetime.timedelta(days=1), table=restaurant_table, restaurant=restaurant, user_id=2, seats=3)
            db.session.add(reservation1)
            db.session.add(reservation2)
            db.session.commit()


    return app


if __name__ == '__main__':
    app = create_app()
    app.run()
