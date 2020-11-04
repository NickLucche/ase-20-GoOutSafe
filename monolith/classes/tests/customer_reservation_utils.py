from monolith.database import db, User, Reservation, Restaurant, RestaurantTable
from monolith.app import create_app
from monolith.classes import customer_reservations as cs
from datetime import datetime, time, date
import random
from flask import Flask

def add_random_users(n: int, app: Flask):
    with app.app_context():
        for i in range(n):
            user = User(email='test',
                        firstname=f'test_{i}',
                        lastname=f'test_{i}',
                        password='test',
                        dateofbirth=datetime.now(),
                        is_active=bool(random.randrange(0, 2)),
                        is_admin=False)
            print(f"Adding user {user.firstname}")
            db.session.add(user)
            db.session.commit()


def delete_random_users(app: Flask):
    with app.app_context():
        delete_query = User.__table__.delete().where(User.email == 'test')
        db.session.execute(delete_query)
        db.session.commit()


def select_user(app: Flask):
    with app.app_context():
        n_users = db.session.query(User).filter_by(is_admin=False).count()
        print(n_users)
        rand_id = random.randint(2, n_users)
        rand_user = db.session.query(User).filter_by(id=rand_id).first()
        print(rand_user)
        return rand_user


def add_random_restaurants(n: int, app: Flask):
    with app.app_context():
        for i in range(n):
            restaurant = Restaurant(name=f'restaurant_{i}',
                                    likes=random.randint(0, 100),
                                    lat=3.131212,
                                    lon=4.125125,
                                    phone=33333333)
            print(f'Adding Restaurant {restaurant.name}')
            db.session.add(restaurant)
            db.session.commit()


def select_restaurant(app: Flask):
    with app.app_context():
        n_restaurants = db.session.query(Restaurant).count()
        rand_id = random.randint(0, n_restaurants)
        rand_restaurant = db.session.query(Restaurant).filter_by(
            id=rand_id).first()
        return rand_restaurant


def add_random_tables(n: int, app: Flask):
    print('Hello I\'m here')
    with app.app_context():
        for i in range(n):
            rand_rest_id = random.randint(0, db.session.query(Restaurant).count())
            #rand_rest_id = 1
            table = RestaurantTable(restaurant_id=rand_rest_id,
                                    seats=random.randint(2, 10))
            print(f'Adding Table {table.table_id}')
            db.session.add(table)
            db.session.commit()


def select_table(app: Flask):
    with app.app_context():
        n_tables = db.session.query(RestaurantTable).count()
        rand_id = random.randint(0, n_tables)
        rand_table = db.session.query(RestaurantTable).filter_by(
            table_id=rand_id).first()
        print(rand_table)
        return rand_table


def delete_random_tables(app: Flask):
    with app.app_context():
        db.session.query(RestaurantTable).delete()
        db.session.commit()


def delete_random_restaurants(app: Flask):
    with app.app_context():
        db.session.query(Restaurant).filter(
            Restaurant.name != 'Trial Restaurant').delete()
        db.session.commit()

def delete_reservations(app):
    with app.app_context(): 
        db.session.query(Reservation).delete()
        db.session.commit()



#app = create_app()
#add_random_restaurants(5, app)
#add_random_tables(10, app)
#delete_reservations(app)
#add_reservations(app)



