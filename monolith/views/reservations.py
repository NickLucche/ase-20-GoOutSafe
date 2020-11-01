from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user, login_required
from monolith.auth import current_user, operator_required
from monolith.database import db, Reservation, RestaurantTable, User, ReservationState
from monolith.classes.reservations import *
import datetime

reservations = Blueprint('reservations', __name__, url_prefix='/reservations')


@reservations.add_app_template_filter
def prettytime(value: datetime.datetime):
    return value.strftime("%A %d %B - %H:%M")


@reservations.add_app_template_test
def modifiable_reservation(reservation: Reservation):
    return reservation.status is not ReservationState.DONE


@reservations.add_app_template_test
def accepted_reservation(reservation: Reservation):
    return reservation.status is ReservationState.ACCEPTED


@reservations.add_app_template_test
def declined_reservation(reservation: Reservation):
    return reservation.status is ReservationState.DECLINED


@reservations.route('/', defaults={'page': 1})
@reservations.route('/page/<int:page>', methods=('GET', ))
@operator_required
def home(page: int):
    reservations, more = get_reservations(current_user.restaurant, num_of_reservations=4, page=page)
    return render_template("reservations.html",
                           reservations=reservations,
                           current_page=page,
                           morepages=more)


@reservations.route('/<id>/decline', methods=('POST', ))
@operator_required
def decline(id: int):
    if decline_reservation(current_user, Reservation.query.filter(Reservation.id == id).first()):
        return redirect(request.referrer)

    return "You are not allowed to do that", 401


@reservations.route('/<id>/accept', methods=('POST', ))
@operator_required
def accept(id: int):
    if accept_reservation(current_user, Reservation.query.filter(Reservation.id == id).first()):
        return redirect(request.referrer)

    return "You are not allowed to do that", 401

