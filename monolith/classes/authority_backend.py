from datetime import datetime, timedelta
from monolith.background import celery
from monolith.database import User
from flask import Flask
from monolith.database import db

# This task is useful for 14 days delayed task
@celery.task
def unmark_user(user_id : int):
    """ Unmakr a single user.
    Args:
        userid (int): Id of the customer to be unmarked
    Returns:
        str: '' in case of success, a error message string in case of failure.
    """
    user = User.query.filter_by(id=user_id).first()
    if user != None and user.is_positive == True:
        user.is_positive = False
        user.reported_positive_date = None
        db.session.commit()
    else:
        message = 'Unable to unmark this user. The user doesn\'t exists or is already not unmarked'

    return message

# This task is useful for crontab temporary execution
@celery.task
def unmark_all(range_days : int):
    """ Unmakr all the users marked more than a certain number of days ago.
    Args:
        range_days (int): Number of days positive users have to be unmarked
    Returns:
        [str]: '' in case of success, a error message string in case of failure.
    """
    print("Crono")
    now = datetime.now()
    time_limit = now - timedelta(days=range_days)
    users = User.query.filter_by(is_positive=True).\
        filter(User.reported_positive_date <= time_limit).all()
    for user in users:
        if user != None and user.is_positive == True:
            user.is_positive = False
            user.reported_positive_date = None
    db.session.commit()

    return ''

@celery.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    print("Crono task configuration")
    # Register the unmark_all as crono task
    sender.add_periodic_task(60.0 * 60.0, unmark_all.s(14), name='unmark_positive')