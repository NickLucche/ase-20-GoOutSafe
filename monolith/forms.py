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
    email = f.StringField('email', validators=[DataRequired()])
    firstname = f.StringField('firstname', validators=[DataRequired()])
    lastname = f.StringField('lastname', validators=[DataRequired()])
    password = f.PasswordField('password', validators=[DataRequired()])
    dateofbirth = f.DateField('dateofbirth', format='%d/%m/%Y')
    display = ['email', 'firstname', 'lastname', 'password', 'dateofbirth']

class ReservationForm(FlaskForm):
    reservation_date = f.DateField('date', validators=[DataRequired(), DateRange(min=datetime.now().date())], format='%d/%m/%Y')
    reservation_time = f.TimeField('time', validators=[DataRequired()])
    seats = f.IntegerField('seats', validators=[DataRequired()])
    display = ['reservation_date', 'reservation_time', 'seats']
    
