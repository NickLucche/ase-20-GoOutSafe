import unittest, datetime
from flask import Flask
from monolith.database import db, User, Restaurant, Reservation, RestaurantTable
from sqlalchemy.schema import MetaData
from pprint import PrettyPrinter
from monolith.classes import reservations


class TestReservations(unittest.TestCase):
    def setUp(self):

        self.data = {}
        self.data['restaurants'] = [
            Restaurant(name="op1 restaurant", likes=1, lat=1, lon=1, phone=1337),
            Restaurant(name="op2 restaurant", likes=3, lat=2, lon=2, phone=1338)
        ]

        self.data['users'] = [
            User(firstname="op1",
                 lastname="op1",
                 email="op1@op1.com",
                 password="op1",
                 restaurant=self.data['restaurants'][0],
                 dateofbirth=datetime.date(2020, 10, 31)),
            User(firstname="op2",
                 lastname="op2",
                 email="op2@op2.com",
                 password="op2",
                 restaurant=self.data['restaurants'][1],
                 dateofbirth=datetime.date(2020, 10, 31))
        ]

        self.data['tables'] = [
            RestaurantTable(seats=3, restaurant=self.data['restaurants'][0]),
            RestaurantTable(seats=5, restaurant=self.data['restaurants'][1])
        ]

        self.app = Flask(__name__)
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

        db.init_app(self.app)
        db.create_all(app=self.app)

        with self.app.app_context():
            for lst in self.data.values():
                db.session.add_all(lst)

            db.session.commit()

            #This has to be declared here otherwise User.id won't be available
            self.data['reservations'] = [
                Reservation(user_id=self.data['users'][0].id,
                            restaurant=self.data['restaurants'][0],
                            table=self.data['tables'][0],
                            reservation_time=datetime.datetime.now() + datetime.timedelta(hours=1),
                            seats=3),
                Reservation(user_id=self.data['users'][1].id,
                            restaurant=self.data['restaurants'][1],
                            table=self.data['tables'][1],
                            reservation_time=datetime.datetime.now() + datetime.timedelta(hours=2),
                            seats=3)
            ]

            db.session.add_all(self.data['reservations'])
            db.session.commit()

    def test_dummy(self):
        pass
        # with self.app.app_context():
        #     meta = MetaData()
        #     meta.reflect(bind=db.engine)
        #     for tbl in meta.tables.values():
        #         stmt = tbl.select()
        #         PrettyPrinter().pprint(db.session.execute(stmt).fetchall())

    def test_get_reservations(self):
        with self.app.app_context():
            restaurants = Restaurant.query.all()
            for restaurant in restaurants:
                rsv, _ = reservations.get_reservations(restaurant)
                for reservation in rsv:
                    #print("{} {}".format(reservation.restaurant_id, restaurant.id))
                    self.assertEqual(reservation.restaurant_id, restaurant.id)
                    self.assertIsNotNone(reservation.user)

    def test_decline_accept_reservations(self):
        with self.app.app_context():
            reservations_list = Reservation.query.all()
            users = User.query.all()
            for reservation in reservations_list:
                if reservation.user is users[0]:
                    ok_user = users[0]
                    failure_user = users[1]
                else:
                    ok_user = users[1]
                    failure_user = users[0]

                self.assertTrue(reservations.decline_reservation(ok_user, reservation))
                self.assertFalse(reservations.decline_reservation(failure_user, reservation))

                self.assertTrue(reservations.accept_reservation(ok_user, reservation))
                self.assertFalse(reservations.accept_reservation(failure_user, reservation))
