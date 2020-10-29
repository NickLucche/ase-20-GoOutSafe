import unittest
from monolith.database import Reservation, db, User, RestaurantTable, Restaurant
import random
from datetime import datetime, timedelta
from monolith.app import create_app
from monolith.classes.tests.reservation_utils import add_random_users, delete_random_users, add_random_restaurants, select_restaurant, add_random_tables, select_table, select_user, delete_random_restaurants, delete_random_tables


class Reservations(unittest.TestCase):
    def test_add_reservation1(self):
        app = create_app()
        add_random_restaurants(5, app)
        add_random_tables(20, app)
        add_random_users(10, app)
        user = select_user(app)
        table = select_table(app)
        today = datetime.now().date()
        time = datetime.now().time()
        with app.app_context():
            r = Reservation()
            r.user_id = user.id
            r.table_no = table.table_id
            r.reservation_date = today
            r.reservation_time = time
            r.restaurant_id = table.restaurant_id
            r.seats = table.seats
            r.entrance_time = False
            db.session.add(r)
            db.session.commit()
            #assert(r.reservation_id)

            reservation_db = db.session.query(Reservation).filter_by(
                reservation_id=r.reservation_id).first()
            print(reservation_db)
            self.assertEqual(r, reservation_db)

        #delete_random_restaurants(app)
        #delete_random_tables(app)
        #delete_random_users(app)


if __name__ == '__main__':
    unittest.main()
