from flask import Blueprint, redirect, render_template, request, url_for, flash
from flask_login import current_user, login_user, logout_user, login_required
from monolith.auth import current_user
from monolith.database import db, Reservation, RestaurantTable, User, ReservationState
from monolith.views.reservations import prettytime
from monolith.classes.customer_reservations import get_user_reservations, delete_reservation
import datetime

customer_reservations = Blueprint('customer_reservations', __name__, url_prefix='/my_reservations')

@customer_reservations.route('/', methods=('GET', ))
@login_required
def get_reservations():
    reservations = get_user_reservations(current_user.id)
    return render_template("customer_reservations.html", reservations = reservations)

@customer_reservations.route('/<reservation_id>/update', methods=('PUT', ))
@login_required
def update_user_reservation(reservation_id: int):
    pass

@customer_reservations.route('/<reservation_id>/delete', methods=('GET', 'DELETE', ))
@login_required
def delete_user_reservation(reservation_id: int):
    if (delete_reservation(reservation_id=reservation_id)):
        flash('Your reservation has been correctly deleted', 'deletion_success')
        return redirect(request.referrer)
    else:
        return render_template("error.html", error_message="You are trying to delete an unexisting reservation.")