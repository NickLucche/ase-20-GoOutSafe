from monolith.classes.exceptions import FormValidationError, UserNotInDB
from flask_login.utils import login_user
from monolith.forms import LoginForm
from monolith.database import db, User

def authenticate_user(form:LoginForm, __submit=True, __password=None):
    """Performs the user authentication if the LoginForm's data are valid.

    Args:
        form (LoginForm): the login form
        __submit (bool, optional): False to not to perform the submit validation (only for tests!). Defaults to True.
        __password (string, optional): The in-clear password used only for test purposes. Defaults to None.

    Raises:
        UserNotInDB: if the user is not registered
        FormValidationError: if the form cannot be validated
    """
    validate = form.validate_on_submit() if __submit else True
    if validate:
        email, password = form.data['email'], form.data['password']
        user = User.query.filter_by(email= email).first()
        if user is not None and user.authenticate(password):
            login_user(user)
            return
        raise UserNotInDB()
    raise FormValidationError()