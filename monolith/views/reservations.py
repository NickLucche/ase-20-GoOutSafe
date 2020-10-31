from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user, login_required
from monolith.auth import current_user, operator_required
from monolith.database import db, Reservation, RestaurantTable, User
from monolith.classes.reservations import *
import datetime

reservations = Blueprint('reservations', __name__, url_prefix='/reservations')


@reservations.add_app_template_filter
def prettytime(value: datetime.datetime):
    return value.strftime("%A %d %B - %H:%M")


@reservations.route('/', methods=('GET', ))
@operator_required
def home():
    reservations = get_reservations(current_user.restaurant)
    return render_template("reservations.html", reservations=reservations)


@reservations.route('/<id>/decline', methods=('POST', ))
@operator_required
def decline(id):
    if decline_reservation(current_user, Reservation.query.filter(Reservation.id == id).first()):
        return redirect(url_for("reservations.home"))
    
    return "You are not allowed to do that", 401
