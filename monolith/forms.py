from flask_wtf import FlaskForm
import wtforms as f
from wtforms.validators import DataRequired


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
    phone_number = f.StringField('Phone number')
    ssn = f.StringField('SSN code')
    display = ['email', 'phone_number', 'ssn']

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
    display = ['l1', 'email', 'firstname', 'lastname', 'password', 'dateofbirth', 'l2',
     'name', 'lat', 'lon', 'phone', 'extra_info']
