from datetime import datetime, time
from werkzeug.security import generate_password_hash, check_password_hash
import enum
from sqlalchemy.orm import relationship
import datetime as dt
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.Unicode(128), nullable=False)
    firstname = db.Column(db.Unicode(128))
    lastname = db.Column(db.Unicode(128))
    password = db.Column(db.Unicode(128))
    dateofbirth = db.Column(db.DateTime)
    fiscal_code = db.Column(db.Text(50), unique=True)
    phone = db.Column(db.Text(50), nullable=True, unique=True)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    is_positive = db.Column(db.Boolean, default=False)
    reported_positive_date = db.Column(db.DateTime, nullable=True)
    is_anonymous = False
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'), nullable=True)
    restaurant = db.relationship("Restaurant", backref=db.backref("restaurant"))
    confirmed_positive_date = db.Column(db.Date, nullable=True)

    def __init__(self, *args, **kw):
        super(User, self).__init__(*args, **kw)
        self._authenticated = False

    def set_password(self, password):
        self.password = generate_password_hash(password)

    @property
    def is_authenticated(self):
        return self._authenticated

    def authenticate(self, password):
        checked = check_password_hash(self.password, password)
        self._authenticated = checked
        return self._authenticated

    def get_id(self):
        return self.id

    def __str__(self) -> str:
        return f'{self.firstname} {self.lastname}--mail:{self.email}--born:{self.dateofbirth.strftime("%B %d %Y")}'

    def to_dict(self):
        return {column.name:getattr(self, column.name) for column in self.__table__.columns}

class Restaurant(db.Model):
    __tablename__ = 'restaurant'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text(100)) 
    likes = db.Column(db.Integer) # will store the number of likes, periodically updated in background
    lat = db.Column(db.Float) # restaurant latitude
    lon = db.Column(db.Float) # restaurant longitude
    phone = db.Column(db.Text)
    extra_info = db.Column(db.Text(300)) # restaurant infos (menu, ecc.)
    avg_stay_time = db.Column(db.Time, default=time(hour=1))

    operator_id = relationship(User, backref="operator")


class Like(db.Model):
    __tablename__ = 'like'

    liker_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    liker = relationship('User', foreign_keys='Like.liker_id')

    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'), primary_key=True)
    restaurant = relationship('Restaurant', foreign_keys='Like.restaurant_id')

    marked = db.Column(db.Boolean, default=False)  # True iff it has been counted in Restaurant.likes


class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    positive_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    date = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    positive_user_reservation = db.Column(db.Integer, db.ForeignKey('reservation.id'))
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'))
    notification_checked = db.Column(db.Boolean, default=False)

    user_notification = db.Column(db.Boolean) # belongs to a user or operator

    def to_dict(self):
        return {column.name:getattr(self, column.name) for column in self.__table__.columns}

class Reservation(db.Model):
    __tablename__ = 'reservation'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = relationship('User', foreign_keys='Reservation.user_id')
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'))
    restaurant = db.relationship("Restaurant", backref=db.backref("restaurant_r"))

    reservation_time = db.Column(db.DateTime, default=datetime.now())
    table_no = db.Column(db.Integer, db.ForeignKey('restaurant_table.table_id'))
    table = db.relationship("RestaurantTable", backref=db.backref("restaurant_table_r"))
    #turn = db.Column(db.Boolean)

    seats = db.Column(db.Integer, default=False)
    entrance_time = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {column.name:getattr(self, column.name) for column in self.__table__.columns}

class RestaurantTable(db.Model):
    __tablename__ = 'restaurant_table'
    table_id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'))
    restaurant = db.relationship("Restaurant", backref=db.backref("restaurant_t"))
    seats = db.Column(db.Integer, default=False)
