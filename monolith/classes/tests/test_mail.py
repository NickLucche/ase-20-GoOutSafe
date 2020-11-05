from monolith.app import create_app
import unittest, datetime
from flask import Flask
from monolith.database import db, User, Notification, Restaurant, User, Reservation
from monolith.classes.mail import send_contact_notification
 
class TestMail(unittest.TestCase):
    def setUp(self):
        
        self.app = create_app()
        self.data = {}

        with self.app.app_context():

            self.user1 = User(firstname="user1",
                 lastname="user1",
                 email="user1@user1",
                 phone='324455551',
                 password="user1",
                 dateofbirth=datetime.date(2020, 10, 31))

            self.user2 = User(firstname="user2",
                 lastname="user2",
                 email="user2@user2.com", #This is the recipient mail address
                 phone='324455552',
                 password="user2",
                 dateofbirth=datetime.date(2020, 10, 31))

            self.restaurant = Restaurant(
                        name = 'restaurant1',
                        lat = '42',
                        lon = '11',
                        phone = '333341548',
                        extra_info = '')
            
            db.session.add(self.user1)
            db.session.add(self.user2)
            db.session.add(self.restaurant)
            db.session.commit()

            self.reservation = Reservation(user_id=self.user1.id,
                                restaurant=self.restaurant,
                                reservation_time=datetime.datetime.now() - datetime.timedelta(hours=1))

            db.session.add(self.reservation)
            db.session.commit()

            #This has to be declared here otherwise User.id won't be available
            self.notification = Notification(positive_user_id = self.user1.id,
                             date = datetime.date(2020, 10, 31),
                             user_id = self.user2.id,
                             positive_user_reservation = self.reservation.id,
                             restaurant_id = self.restaurant.id,
                             notification_checked = False,
                             email_sent = False,
                             user_notification = True)
                
            db.session.add(self.notification)
            db.session.commit()

    def test_send_mail(self):
        with self.app.app_context():
            send_contact_notification()

            #check the notification has the field email_sent correctly set to true
            self.assertEqual(len(Notification.query.filter_by(email_sent=True).all()), 1)
            self.assertEqual(len(Notification.query.filter_by(email_sent=False).all()), 0)

            db.session.query(Notification).delete()
            db.session.query(Reservation).delete()
            db.session.query(Restaurant).delete()
            db.session.query(User).delete()
            db.session.commit()

    def test_clean(self):
        with self.app.app_context():
            db.session.query(Notification).delete()
            db.session.query(Reservation).delete()
            db.session.query(Restaurant).delete()
            db.session.query(User).delete()
            db.session.commit()