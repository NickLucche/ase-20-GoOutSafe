from operator import add
import unittest, datetime, logging
from monolith.app import create_app
from monolith.database import Restaurant, User, db

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()

user_data = {'email':'prova@prova.com', 
        'firstname':'Mario', 
        'lastname':'Rossi', 
        'dateofbirth':datetime.datetime(1990, 12, 3)}
user_clear_pass = "pass"

restaurant_data = {'name': 'Mensa martiri', 
                    'lat': '4.12345',
                    'lon': '5.67890',
                    'phone': '3333333333',
                    'extra_info': 'Rigatoni dorati h24, cucina povera'}

def add_testuser():
    u = User(**user_data)
    u.set_password(user_clear_pass)
    return u

class TestUsers(unittest.TestCase):
    def test_createuser(self):
        app = create_app()
        with app.app_context():
            u = add_testuser()
            db.session.add(u)
            db.session.commit()
            assert(u.id)
            
            user_in_db = User.query.get(u.id)
            assert(u == user_in_db)
            User.query.filter(User.id == u.id).delete()
            db.session.commit()
        return

    def test_createoperator(self):
        app = create_app()
        with app.app_context():
            r = Restaurant(**restaurant_data)
            db.session.add(r)
            db.session.flush() # getting r's primary key
            assert(r.id)
            u = add_testuser()
            u.restaurant_id = r.id
            db.session.add(u)
            db.session.commit()
            assert(u.restaurant_id == r.id)

            added_r = Restaurant.query.get(r.id)
            added_u = User.query.get(u.id)
            assert(added_r == r and added_u == u)
            
            User.query.filter(User.id == u.id).delete()
            Restaurant.query.filter(Restaurant.id == r.id).delete()
            db.session.commit()
            
if __name__ == "__main__":
    unittest.main()