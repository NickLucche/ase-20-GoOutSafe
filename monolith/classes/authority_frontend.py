from datetime import datetime, timedelta
from monolith.database import db, User

def mark_user(user_id: int):
    """ Mark a user as positive.
    Args:
        userid (int): Id of the customer
    Returns:
        str: '' in case of success, a error message string in case of failure.
    """
    user = User.query.filter_by(id=user_id).first()
    
    if user == None:
        message = 'Error! Unable to mark the user. User not found'
    elif user.is_positive == False:
        user.is_positive = True
        user.reported_positive_date = datetime.now()
        db.session.commit()
        message = ''
        # Here the 14 days celery task has to be started
    else:
        message = 'You\'ve already marked this user as positive!'

    return message

