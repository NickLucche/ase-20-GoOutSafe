import unittest, datetime
from flask import Flask
from monolith.database import db, User, Restaurant, Reservation, RestaurantTable, ReservationState
from sqlalchemy.schema import MetaData
from pprint import PrettyPrinter
from monolith.classes import reservations
from monolith.views import reservations as reservations_view


class TestReservations(unittest.TestCase):
    def setUp(self):

        self.data = {}
        self.data['restaurants'] = [
            Restaurant(name="op1 restaurant", likes=1, lat=1, lon=1, phone='6969696'),
            Restaurant(name="op2 restaurant", likes=3, lat=2, lon=2, phone='969696')
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
            RestaurantTable(table_id=1, seats=3, restaurant=self.data['restaurants'][0]),
            RestaurantTable(table_id=1, seats=5, restaurant=self.data['restaurants'][1])
        ]

        self.app = Flask(__name__)
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
        self.app.register_blueprint(reservations_view)

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
                            reservation_time=datetime.datetime.now() + datetime.timedelta(minutes=1),
                            status=ReservationState.ACCEPTED,
                            seats=3),
                Reservation(user_id=self.data['users'][1].id,
                            restaurant=self.data['restaurants'][1],
                            table=self.data['tables'][1],
                            reservation_time=datetime.datetime.now() + datetime.timedelta(minutes=2),
                            status=ReservationState.DECLINED,
                            seats=3),
                Reservation(user_id=self.data['users'][1].id,
                            restaurant=self.data['restaurants'][1],
                            table=self.data['tables'][1],
                            status=ReservationState.ACCEPTED,
                            reservation_time=datetime.datetime.now() - datetime.timedelta(minutes=2),
                            seats=3),
                Reservation(user_id=self.data['users'][1].id,
                            restaurant=self.data['restaurants'][1],
                            table=self.data['tables'][1],
                            status=ReservationState.SEATED,
                            reservation_time=datetime.datetime.now() - datetime.timedelta(minutes=2),
                            seats=3),
                Reservation(user_id=self.data['users'][1].id,
                            restaurant=self.data['restaurants'][1],
                            table=self.data['tables'][1],
                            status=ReservationState.DONE,
                            reservation_time=datetime.datetime.now() - datetime.timedelta(minutes=2),
                            seats=3),
                Reservation(user_id=self.data['users'][1].id,
                            restaurant=self.data['restaurants'][1],
                            table=self.data['tables'][1],
                            status=ReservationState.DONE,
                            reservation_time=datetime.datetime(2020, 10, 31),
                            seats=3),
                Reservation(user_id=self.data['users'][1].id,
                            restaurant=self.data['restaurants'][1],
                            table=self.data['tables'][1],
                            status=ReservationState.DONE,
                            reservation_time=datetime.datetime(2020, 10, 31),
                            seats=3),
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

    def test_jinja_tests(self):
        with self.app.app_context():
            reservations_list = Reservation.query.all()
            test_dict = self.app.jinja_env.tests

            self.assertTrue(test_dict['modifiable_reservation'](reservations_list[0]))
            self.assertFalse(test_dict['modifiable_reservation'](reservations_list[2]))

            self.assertTrue(test_dict['accepted_reservation'](reservations_list[0]))
            self.assertFalse(test_dict['accepted_reservation'](reservations_list[1]))

            self.assertTrue(test_dict['declined_reservation'](reservations_list[1]))
            self.assertFalse(test_dict['declined_reservation'](reservations_list[0]))

            self.assertTrue(test_dict['show_mark_buttons'](reservations_list[3]))
            self.assertFalse(test_dict['show_mark_buttons'](reservations_list[1]))

            self.assertTrue(test_dict['entrance_marked'](reservations_list[3]))
            self.assertFalse(test_dict['entrance_marked'](reservations_list[2]))

            self.assertTrue(test_dict['exit_marked'](reservations_list[4]))
            self.assertFalse(test_dict['exit_marked'](reservations_list[3]))

    def test_jinja_filters(self):
        with self.app.app_context():
            reservations_list = Reservation.query.all()
            filters_dict = self.app.jinja_env.filters

            self.assertEqual(filters_dict['prettytime'](datetime.datetime(2020, 10, 31, 0, 0)),
                             "Saturday 31 October - 00:00")
            self.assertEqual(filters_dict['prettyhour'](datetime.datetime(2020, 10, 31, 0, 0)), "00:00")

    def test_mark_entrance(self):
        with self.app.app_context():
            reservations_list = Reservation.query.all()
            users = User.query.all()

            self.assertFalse(reservations.reservation_mark_entrance(users[0], reservations_list[0]))
            self.assertTrue(reservations.reservation_mark_entrance(users[1], reservations_list[2]))
            self.assertFalse(reservations.reservation_mark_entrance(users[1], reservations_list[4]))

    def test_mark_exit(self):
        with self.app.app_context():
            reservations_list = Reservation.query.all()
            users = User.query.all()

            self.assertFalse(reservations.reservation_mark_exit(users[0], reservations_list[0]))
            self.assertTrue(reservations.reservation_mark_exit(users[1], reservations_list[3]))
            self.assertFalse(reservations.reservation_mark_exit(users[1], reservations_list[4]))

    def test_get_reservations_of_the_day(self):
        with self.app.app_context():
            users = User.query.all()
            reservations_list, more = reservations.get_reservations_of_the_day(users[1].restaurant, 30, 1);

            self.assertEqual(len(reservations_list), 4)
            self.assertFalse(more)

    def test_get_seated_customers(self):
        with self.app.app_context():
            users = User.query.all()

            self.assertEqual(reservations.get_seated_customers(users[1].restaurant), 3)

