from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user, login_required
from monolith.auth import current_user
from monolith.database import db, Reservation, RestaurantTable, User, ReservationState
from monolith.views.reservations import prettytime
from monolith.classes.customer_reservations import get_user_reservations
import datetime

customer_reservations = Blueprint('customer_reservations', __name__, url_prefix='/reservations/user')

@customer_reservations.route('/<user_id>', methods=('GET', ))
def get_reservations(user_id: int, message=''):
    reservations = get_user_reservations(user_id)
    return render_template("customer_reservations.html", reservations = reservations, message=message)

@customer_reservations.route('/<user_id>/modify/<reservation_id>', methods=('PUT', ))
def modify_reservation(reservation_id: int):
    pass

@customer_reservations.route('/<user_id>/delete/<reservation_id>', methods=('DELETE', ))
def delete_reservation(reservation_id: int):
    pass