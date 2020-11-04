from monolith.classes.exceptions import FormValidationError, UserNotInDB
from flask_login.utils import login_user
from monolith.forms import LoginForm
from monolith.database import db, User

def authenticate_user(form:LoginForm, __submit=True, __password=None):
    validate = form.validate_on_submit() if __submit else True
    if validate:
        email, password = form.data['email'], form.data['password']
        user = User.query.filter_by(email= email).first()
        if user is not None and user.authenticate(password):
            login_user(user)
            return
        raise UserNotInDB()
    raise FormValidationError()