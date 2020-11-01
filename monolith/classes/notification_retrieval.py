from datetime import datetime, timedelta
from monolith.database import Notification, User
from flask import Flask
from sqlalchemy import desc, distinct

def fetch_user_notifications(app: Flask, user_id: int, unread_only=False):
    """Retrieve 'positive case contact' notifications of user identified by `user_id`.
    Args:
        app (Flask): flask app.
        user_id (int): identifier of user requesting notifications.
        unread_only (bool, optional): Whether to retrieve unread notifications only. Defaults to False.
    """
    with app.app_context():
        query = Notification.query.filter_by(user_id=user_id)
        if unread_only:
            query = query.filter_by(notification_checked=False)
        query = query.order_by(desc(Notification.date))
        
        return query.all()

def fetch_operator_notifications(app:Flask, rest_id: int, unread_only=False):
    # get notifications belonging to a certain restaurant
    with app.app_context():
        # query = Reservation.query.join(Notification)\
        query = Notification.query.filter_by(restaurant_id=rest_id, user_notification=False)
            
        if unread_only:
            query = query.filter_by(notification_checked=False)

        # query = query.with_entities(Reservation, Notification)
        query = query.order_by(desc(Notification.date))

        return [q.to_dict() for q in query.all()]

def fetch_notifications(app: Flask, user: User, unread_only=False):
    """Fetch notifications of operator or user alike.
    Args:
        app (Flask): [description]
        user_id ([type]): [description]
    """
    if hasattr(user, 'restaurant_id') and not user.restaurant_id is None:
        return fetch_operator_notifications(app, user.id, unread_only)
    else:
        return fetch_user_notifications(app, user.id, unread_only)