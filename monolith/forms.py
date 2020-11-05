from flask_sqlalchemy.utils import parse_version
from flask_wtf import FlaskForm
import wtforms as f
from datetime import datetime
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange, Optional
from wtforms.fields.html5 import DateField
from wtforms_components import DateRange


class LoginForm(FlaskForm):
    email = f.StringField('email', validators=[DataRequired(), Email(message="Please enter a valid email")])
    password = f.PasswordField('password', validators=[DataRequired()])
    display = ['email', 'password']


class UserForm(FlaskForm):
    email = f.StringField('e-mail', validators=[DataRequired(), Email(message="Please enter a valid email")])
    firstname = f.StringField('Name', validators=[DataRequired()])
    lastname = f.StringField('Last name', validators=[DataRequired()])
    password = f.PasswordField('Password', validators=[DataRequired(), EqualTo('password_confirm', message='Passwords must match')])
    password_confirm = f.PasswordField('Confirm password', validators=[DataRequired()])
    fiscal_code = f.StringField('Insert your fiscal code', \
        validators=[DataRequired(), Length(min=16, max=16, message="Fiscal code length is invalid")], \
            render_kw={"maxlength": "16"})
    phone = f.IntegerField('(optional) Phone number', validators=[Optional()], render_kw={"minlength":"9", "maxlength": "10"})

    dateofbirth = DateField('Date of Birth', format='%Y-%m-%d', validators=[DataRequired()])
    display = ['email', 'firstname', 'lastname', 'password', 'password_confirm', 'fiscal_code', 'phone', 'dateofbirth']


class SearchUserForm(FlaskForm):
    email = f.StringField('email', validators=[Email(message="Please enter a valid email")])
    phone = f.StringField('Phone number')
    fiscal_code = f.StringField('Fiscal code')
    display = ['email', 'phone', 'fiscal_code']


class OperatorForm(FlaskForm):
    l1 = f.Label('Owner infos', 'Owner infos')
    email = f.StringField('e-mail', validators=[DataRequired(), Email(message="Please enter a valid email")])
    firstname = f.StringField('Name', validators=[DataRequired()])
    lastname = f.StringField('Last name', validators=[DataRequired()])
    password = f.PasswordField('Password', validators=[DataRequired(), \
        Length(min=4, max=12, message="Password must be in [4,12] characters"), EqualTo('password_confirm', message='Passwords must match')])
    password_confirm = f.PasswordField('Confirm password', validators=[DataRequired()])
    dateofbirth = DateField('Date of birth', format='%Y-%m-%d', validators=[DataRequired()])
    h1 = f.HiddenField()
    l2 = f.Label('', 'Restaurant info')
    name = f.StringField('Name', validators=[DataRequired()])
    lat = f.FloatField('Latitude', validators=[DataRequired(), NumberRange(min=-90, max=90, message="Latitude is in [-90, 90]")])
    lon = f.FloatField('Longitude', validators=[DataRequired(), NumberRange(min=-180, max=180, message="Longitude is in [-180, 180]")])
    phone = f.IntegerField('Phone number', validators=[DataRequired()], render_kw={"minlength":"9", "maxlength": "10"})
    extra_info = f.TextAreaField('Extra infos [optional]')
    display = [
        'l1', 'email', 'firstname', 'lastname', 'password', 'password_confirm', 'dateofbirth', 'l2', 'name', 'lat', 'lon', 'phone',
        'extra_info'
    ]


class RestaurantProfileEditForm(FlaskForm):
    name = f.StringField('Name', validators=[DataRequired()])
    lat = f.FloatField('Latitude', validators=[DataRequired()])
    lon = f.FloatField('Longitude', validators=[DataRequired()])
    phone = f.IntegerField('Phone number', validators=[DataRequired()], render_kw={"minlength":"9", "maxlength": "10"})
    extra_info = f.TextAreaField('Extra info')
    display = ['name', 'lat', 'lon', 'phone', 'extra_info']

class UserProfileEditForm(FlaskForm):
    email = f.StringField('e-mail', validators=[DataRequired(), Email(message="Please enter a valid email")])
    password = f.PasswordField('New password', validators=[Optional(), EqualTo('password_confirm', message='Passwords must match')], \
        render_kw={"minlength":"4", "maxlength": "12"})
    password_confirm = f.PasswordField('Confirm new password', validators=[Optional()])
    phone = f.IntegerField('(optional) Phone number', validators=[Optional()], render_kw={"minlength":"9", "maxlength": "10"})
    display = ['email', 'password', 'password_confirm', 'phone']

class ReservationForm(FlaskForm):
    reservation_date = f.DateField('date',
                                   validators=[DataRequired(), DateRange(min=datetime.now().date())],
                                   format='%d/%m/%Y', render_kw={"type":"date"})
    reservation_time = f.TimeField('time', validators=[DataRequired()])
    seats = f.IntegerField('seats', validators=[DataRequired()])
    display = ['reservation_time', 'reservation_time', 'seats']

class RatingForm(FlaskForm): 
    review = f.TextAreaField(validators=[Optional()], render_kw={"placeholder":"(optional) Add a written review!"})  
    submit = f.SubmitField('Submit') 
    display = ['review', 'submit']
