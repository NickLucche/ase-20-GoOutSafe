from datetime import datetime, timedelta
from monolith.background import celery
from monolith.database import Restaurant, User, Reservation, Notification
from flask import Flask
from monolith.database import db

# tasks are written so that pipeline|chain async execution is easily implemented

@celery.task
# only accept serializable args
def check_visited_places(userid: int, day_range: int):
    """ Checks the restaurants in which a given customer has been to
        in the last `day_range` days.
    Args:
        userid (int): Id of the customer
        day_range (int): Number of days in which we're checking the customer activities.
    Returns:
        [type]: A list of restaurants or an empty list in case the customer didn't visit
        any restaurant.
    """
    print(f"Checking visited places by user {userid} in the last {day_range} days")
    # get reservations in which user actually showed up
    range = datetime.now() - timedelta(days=day_range)
    range.replace(hour=0, minute=0, second=0, microsecond=0)
    
    reservations = Reservation.query.filter_by(user_id=userid).\
    filter(Reservation.entrance_time != None).filter(Reservation.entrance_time >= range).all()
    print(reservations)
    # also all results must be json serializable
    return [row.to_dict() for row in reservations]

@celery.task
def create_notifications(reservation_at_riks, positive_id: int):
    """[summary]

    Args:
        positive_id (str): [description]
        reservation_at_riks ([type]): [description]
    """
    # create multiple notification even if the user visited the same restaurant in multiple occasions (can group'em later)
    notifications = []
    for reservation in reservation_at_riks:
        rest_id = reservation['restaurant_id']
        customer_id = reservation['user_id']
        # when function is called without celery, there's no need to serialize to JSON
        et = reservation['entrance_time']
        if isinstance(et, str):
            et = datetime.strptime(reservation['entrance_time'], '%Y-%m-%dT%H:%M:%S.%f')
        
        # create notification
        notification = Notification(positive_user_id=positive_id, restaurant_id=rest_id,
        date=et, user_id = customer_id)
        notifications.append(notification)
    # store in database
    db.session.add_all(notifications)
    db.session.commit()
    return [n.to_dict() for n in notifications]
        

@celery.task
def contact_tracing(past_reservations, user_id: int):
    """Given a positive user id and a list of past reservation he/she made in the last 14 days,
        returns a list of reservation made by users which were allegedly in contact with him/her.

    Args:
        user_id (int): Positive customer id.
        past_reservations: List of dictionaries, each representing a reservation the positive 
        user made.
    """
    # check which users were at the restaurant at the same time as the positive guy (by checking the turn)
    print("INPUT", past_reservations, user_id)
    reservation_at_risk = []
    for reservation in past_reservations:
        et = reservation['entrance_time']
        if isinstance(et, str):
            et = datetime.strptime(reservation['entrance_time'], '%Y-%m-%dT%H:%M:%S.%f')
        start_of_day = datetime(et.year, et.month, et.day)
        end_of_day = datetime(et.year, et.month, et.day, 23, 59, 59, 59)
        # TODO: add distinct
        user_reservation = Reservation.query.filter(Reservation.user_id != user_id).\
            filter_by(restaurant_id=reservation['restaurant_id'], turn=reservation['turn']).\
                filter(Reservation.entrance_time.between(start_of_day, end_of_day)).all()
        print(user_reservation)
        reservation_at_risk += user_reservation
    return [u.to_dict() for u in reservation_at_risk]

def fetch_user_notifications(user_id: str):
    pass

def fetch_operator_notifications(user_id: str):
    pass