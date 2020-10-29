from flask import Flask, current_app
from monolith.database import db, User, Restaurant, Reservation, RestaurantTable


def get_reservations(restaurant: Restaurant):
    """
    Gets all the restaurant reservations
    """
    reservations = db.session.query(Reservation).filter(Reservation.restaurant_id == restaurant.id).all()
    return reservations
