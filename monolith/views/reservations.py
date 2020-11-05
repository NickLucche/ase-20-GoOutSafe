from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user, login_required
from monolith.auth import current_user, operator_required
from monolith.database import db, Reservation, RestaurantTable, User, ReservationState
from monolith.classes.reservations import *
import datetime

reservations = Blueprint('reservations', __name__, url_prefix='/reservations')


@reservations.add_app_template_filter
def prettytime(value: datetime.datetime):
    """
    Pretty printing of date and time.
    """
    return value.strftime("%A %d %B - %H:%M")


@reservations.add_app_template_filter
def prettyhour(value: datetime.datetime):
    """
    Pretty printing of time only.
    """
    return value.strftime("%H:%M")


@reservations.add_app_template_test
def modifiable_reservation(reservation: Reservation):
    """
    Returns true iff the reservation is still modifiable, i.e. if the reservation time is not yet due.
    """
    return reservation.reservation_time > datetime.datetime.now()


@reservations.add_app_template_test
def accepted_reservation(reservation: Reservation):
    """
    Returns true iff the reservation has been accepted.
    """
    return reservation.status is ReservationState.ACCEPTED


@reservations.add_app_template_test
def declined_reservation(reservation: Reservation):
    """
    Returns true iff the reservation has been declined.
    """
    return reservation.status is ReservationState.DECLINED


@reservations.add_app_template_test
def show_mark_buttons(reservation: Reservation):
    """
    Returns true iff the mark buttons have to be shown, i.e. if the reservation is atleast accepted and it is past due.
    """
    return reservation.status.value > ReservationState.PENDING and reservation.reservation_time <= datetime.datetime.now()


@reservations.add_app_template_test
def entrance_marked(reservation: Reservation):
    """
    Returns true if the entrance has been marked.
    """
    return reservation.status.value >= ReservationState.SEATED.value


@reservations.add_app_template_test
def exit_marked(reservation: Reservation):
    """
    Returns true if the exit has been marked.
    """
    return reservation.status is ReservationState.DONE


@reservations.route('/', defaults={'page': 1})
@reservations.route('/page/<int:page>', methods=('GET', ))
@operator_required
def home(page: int):
    reservations, more = get_reservations(current_user.restaurant, num_of_reservations=6, page=page)
    if not reservations and page > 1:
        return "", 404
    else:
        return render_template("reservations.html",
                               reservations=reservations,
                               current_page=page,
                               morepages=more,
                               customers=get_seated_customers(current_user.restaurant),
                               today=False)


@reservations.route('/today', defaults={'page': 1})
@reservations.route('/today/page/<int:page>', methods=('GET', ))
@operator_required
def today(page: int):
    reservations, more = get_reservations_of_the_day(current_user.restaurant, num_of_reservations=6, page=page)
    if not reservations and page > 1:
        return "", 404
    else:
        return render_template("reservations.html",
                               reservations=reservations,
                               current_page=page,
                               morepages=more,
                               customers=get_seated_customers(current_user.restaurant),
                               today=False)


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


@reservations.route('/<id>/markentrance', methods=('POST', ))
@operator_required
def mark_entrance(id: int):
    if reservation_mark_entrance(current_user, Reservation.query.filter(Reservation.id == id).first()):
        return redirect(request.referrer)

    return "You are not allowed to do that", 401


@reservations.route('/<id>/markexit', methods=('POST', ))
@operator_required
def mark_exit(id: int):
    if reservation_mark_exit(current_user, Reservation.query.filter(Reservation.id == id).first()):
        return redirect(request.referrer)

    return "You are not allowed to do that", 401
