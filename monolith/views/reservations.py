from flask import Blueprint, redirect, render_template, request
from flask_login import current_user, login_user, logout_user, login_required
from monolith.auth import current_user, operator_required
from monolith.database import db, Reservation, RestaurantTable, User
from monolith.classes.reservations import *

reservations = Blueprint('reservations', __name__, url_prefix='/reservations')


@reservations.route('/', methods=('GET', 'POST'))
@operator_required
def home():
    reservations = get_reservations(current_user.restaurant)
    return render_template("reservations.html", reservations=reservations)