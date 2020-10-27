from datetime import datetime, timedelta
from monolith.background import celery
from monolith.database import User, Reservation
from flask import Flask


@celery.task
def check_visited_places(user: User, day_range: int, app: Flask):
    print(f"Checking visited places by user {user} in the last {day_range} days")
    # get reservations in which user actually showed up
    range = datetime.now() - timedelta(days=day_range)
    range.replace(hour=0, minute=0, second=0, microsecond=0)
    with app.app_context():
        reservations = Reservation.query.filter_by(user_id=user.id).\
        filter(Reservation.entrance_time != None).filter(Reservation.entrance_time >= range).all()
        print(reservations)
    return reservations
