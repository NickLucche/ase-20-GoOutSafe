from flask import Flask, current_app
from monolith.database import db, User, Restaurant, Reservation, RestaurantTable, ReservationState


def get_reservations(restaurant: Restaurant, num_of_reservations: int = 30, page: int = 1):
    """
    Gets all the restaurant reservations
    """
    reservations = Reservation.query.filter(Reservation.restaurant == restaurant).offset(
        (page - 1) * num_of_reservations).limit(num_of_reservations + 1).all()

    more = len(reservations) > num_of_reservations
    reservations.pop() if more else None

    return reservations, more


def decline_reservation(user: User, reservation: Reservation):
    """
    Decline a reservation
    """
    owns_restaurant = reservation.restaurant.operator == user
    if owns_restaurant:
        #Might want to add user notification
        reservation.status = ReservationState.DECLINED
        db.session.commit()
        return True

    return False


def accept_reservation(user: User, reservation: Reservation):
    """
    Accept a reservation
    """
    owns_restaurant = reservation.restaurant.operator == user
    if owns_restaurant:
        #Might want to add user notification
        reservation.status = ReservationState.ACCEPTED
        db.session.commit()
        return True

    return False
