from flask import Flask, current_app
from monolith.database import db, User, Restaurant, Reservation, RestaurantTable


def get_reservations(restaurant: Restaurant):
    """
    Gets all the restaurant reservations
    """
    reservations = db.session.query(Reservation, User).filter(Reservation.restaurant_id == restaurant.id).join(
        User, User.id == Reservation.user_id).all()
    return reservations


def decline_reservation(user: User, reservation: Reservation):
    """
    Decline a reservation
    """
    owns_restaurant = User.query.filter(User.restaurant_id == reservation.restaurant_id,
                                        User.id == user.id).first() is not None
    if owns_restaurant:
        #Might want to add user notification
        db.session.delete(reservation)
        db.session.commit()
        return True
    
    return False
