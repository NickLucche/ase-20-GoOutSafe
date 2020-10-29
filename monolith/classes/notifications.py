from datetime import datetime, timedelta
from monolith.background import celery
from monolith.database import User, Reservation
from flask import Flask
from monolith.app import create_app



@celery.task
# only accept serializable args
def check_visited_places(userid: int, day_range: int):
    app = create_app()
    print(f"Checking visited places by user {userid} in the last {day_range} days")
    # get reservations in which user actually showed up
    range = datetime.now() - timedelta(days=day_range)
    range.replace(hour=0, minute=0, second=0, microsecond=0)
    with app.app_context():
        reservations = Reservation.query.filter_by(user_id=userid).\
        filter(Reservation.entrance_time != None).filter(Reservation.entrance_time >= range).all()
        print(reservations)
    # also all results must be json serializable
    return [r.user_id for r in reservations]
