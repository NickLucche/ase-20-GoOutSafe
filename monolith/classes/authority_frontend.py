from datetime import datetime, timedelta
from sqlalchemy import func
from monolith.database import db, User

INCUBATION_PERIOD_COVID = 14

def mark_user(user_id: int):
    """ Mark a user as positive.
    Args:
        userid (int): Id of the customer
    Returns:
        str: '' in case of success, a error message string in case of failure.
    """
    user = User.query.filter_by(id=user_id).first()
    user_dict = None
    if user == None:
        message = 'Error! Unable to mark the user. User not found'
    elif user.is_positive == False:
        user.is_positive = True
        user.reported_positive_date = datetime.now()
        user_dict = user.to_dict()
        db.session.commit()
        message = ''
        
        from monolith.classes.authority_backend import new_positive_case
        new_positive_case(user_id)
    else:
        message = 'You\'ve already marked this user as positive!'

    return message, user_dict

def search_user(filter_user: User):
    if filter_user.email == '' and filter_user.fiscal_code == '' and filter_user.phone == '':
        return None, 'At least one in fiscal code, email or phone number is required'

    if filter_user.phone != None and filter_user.phone != '' and len(filter_user.phone) < 9:
        return None, 'Invalid phone number'

    if filter_user.fiscal_code != None and filter_user.fiscal_code != '' and len(filter_user.fiscal_code) != 16:
        return None, 'Invalid fiscal code'
    
    q = db.session.query(User)

    #if filter_user.firstname != "":
    #    q = q.filter(func.lower(User.firstname) == func.lower(filter_user.firstname))
    #if filter_user.lastname != "":
    #    q = q.filter(func.lower(User.lastname) == func.lower(filter_user.lastname))
    if filter_user.email != None and filter_user.email != '':
        q = q.filter(func.lower(User.email) == func.lower(filter_user.email))
    if filter_user.phone != None and filter_user.phone != '':
        q = q.filter(User.phone == filter_user.phone)
    if filter_user.fiscal_code != None and filter_user.fiscal_code != '':
        q = q.filter(func.upper(User.fiscal_code) == func.upper(filter_user.fiscal_code))

    if q.first() == None:
        return None, 'No user found'
    else:
        return q.first(), 'OK'