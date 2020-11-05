from werkzeug.utils import validate_arguments
from monolith.classes.exceptions import DatabaseError, FormValidationError
from monolith.forms import OperatorForm, UserForm, UserProfileEditForm
from monolith.database import Restaurant, db, User

def _check_user_not_in_db(email):
    """Check if an user is not in db (not registered).

    Args:
        email (string): the user email

    Raises:
        DatabaseError: if an user with the same email already exists
    """
    u = User.query.filter_by(email=email).scalar()
    if u != None:
        raise DatabaseError("An user with the same email already exists!")

def _create_user_obj(form : UserForm, password) -> User:
    """Creates a new user from the form data.

    Args:
        form (UserForm): the form
        password (string): the password

    Returns:
        User: the user object
    """
    u = User()
    form.populate_obj(u)
    u.set_password(password) #pw should be hashed with some salt
    return u

def users_view():
    return db.session.query(User)

def new_user(form : UserForm, __submit=True, __password=''):
    """Manages the user registration.

    Args:
        form (UserForm): the registration form
        __submit (bool, optional): False to not to perform the submit validation (only for tests!). Defaults to True.
        __password (string, optional): The in-clear password used only for test purposes. Defaults to None.

    Raises:
        FormValidationError: if the form cannot be validated
    Returns:
        User: the new user, if any
    """
    validate = form.validate_on_submit() if __submit else True
    if __submit:
        __password = form.password.data
    if validate:
        _check_user_not_in_db(form.email.data)

        new_user = _create_user_obj(form, __password)
        db.session.add(new_user)
        db.session.commit()
        return new_user
    raise FormValidationError("Error validating the form: " + str(form.errors))

def new_operator(form: OperatorForm, __submit=True, __password=''):
    """Manages the operator/restaurant registration.

    Args:
        form (OperatorForm): the registration form
        __submit (bool, optional): False to not to perform the submit validation (only for tests!). Defaults to True.
        __password (string, optional): The in-clear password used only for test purposes. Defaults to None.

    Raises:
        FormValidationError: if the form cannot be validated
    Returns:
        User: the new user, if any
    """
    validate = form.validate_on_submit() if __submit else True
    if __submit:
        __password = form.password.data
    if validate:
        _check_user_not_in_db(form.email.data)

        new_user = _create_user_obj(form, __password)
        new_restaurant = Restaurant()
        form.populate_obj(new_restaurant)
        new_user.is_operator = True
        db.session.add(new_restaurant)
        db.session.flush()
        new_user.restaurant_id = new_restaurant.id
        db.session.add(new_user)
        db.session.commit()
        return new_user
    raise FormValidationError("Error validating the form")

def edit_user_data(form:UserProfileEditForm, user_id, __submit=True):
    """Manages the user data editing.

    Args:
        form (UserProfileEditForm): the editing form
        user_id (int): the user id
        __submit (bool, optional): False to not to perform the submit validation (only for tests!). Defaults to True.

    Raises:
        FormValidationError: if the form cannot be validated
    """
    validate = form.validate_on_submit() if __submit else True
    if validate:
        u = User.query.filter_by(id=user_id).first()
        
        form.populate_obj(u)
        if form.password is not None and form.password.data != '':
            u.set_password(str(form.password.data))
        db.session.commit()
    else:
        raise FormValidationError("Error validating the form")
