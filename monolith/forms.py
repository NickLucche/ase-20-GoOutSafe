from flask_wtf import FlaskForm
import wtforms as f
from datetime import datetime
from wtforms.validators import DataRequired
from wtforms_components import DateRange


class LoginForm(FlaskForm):
    email = f.StringField('email', validators=[DataRequired()])
    password = f.PasswordField('password', validators=[DataRequired()])
    display = ['email', 'password']


class UserForm(FlaskForm):
    email = f.StringField('e-mail', validators=[DataRequired()])
    firstname = f.StringField('Name', validators=[DataRequired()])
    lastname = f.StringField('Last name', validators=[DataRequired()])
    password = f.PasswordField('Password', validators=[DataRequired()])
    dateofbirth = f.DateField('Date of Birth', format='%d/%m/%Y')
    display = ['email', 'firstname', 'lastname', 'password', 'dateofbirth']


class SearchUserForm(FlaskForm):
    email = f.StringField('email')
    firstname = f.StringField('firstname')
    lastname = f.StringField('lastname')
    display = ['email', 'firstname', 'lastname']


class OperatorForm(FlaskForm):
    l1 = f.Label('Owner infos', 'Owner infos')
    email = f.StringField('e-mail', validators=[DataRequired()])
    firstname = f.StringField('Name', validators=[DataRequired()])
    lastname = f.StringField('Last name', validators=[DataRequired()])
    password = f.PasswordField('Password', validators=[DataRequired()])
    dateofbirth = f.DateField('Date of birth', format='%d/%m/%Y')
    h1 = f.HiddenField()
    l2 = f.Label('', 'Restaurant info')
    name = f.StringField('Name', validators=[DataRequired()])
    lat = f.FloatField('Latitude', validators=[DataRequired()])
    lon = f.FloatField('Longitude', validators=[DataRequired()])
    phone = f.IntegerField('Phone number', validators=[DataRequired()])
    extra_info = f.TextAreaField('Extra infos [optional]')
    display = [
        'l1', 'email', 'firstname', 'lastname', 'password', 'dateofbirth', 'l2', 'name', 'lat', 'lon', 'phone',
        'extra_info'
    ]


class RestaurantProfileEditForm(FlaskForm):
    name = f.StringField('Name', validators=[DataRequired()])
    lat = f.FloatField('Latitude', validators=[DataRequired()])
    lon = f.FloatField('Longitude', validators=[DataRequired()])
    phone = f.IntegerField('Phone number', validators=[DataRequired()])
    extra_info = f.TextAreaField('Extra info')
    display = ['name', 'lat', 'lon', 'phone', 'extra_info']


class ReservationForm(FlaskForm):
    reservation_date = f.DateField('date',
                                   validators=[DataRequired(), DateRange(min=datetime.now().date())],
                                   format='%d/%m/%Y')
    reservation_time = f.TimeField('time', validators=[DataRequired()])
    seats = f.IntegerField('seats', validators=[DataRequired()])
    display = ['reservation_date', 'reservation_time', 'seats']
