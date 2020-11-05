from flask import Blueprint, redirect, render_template, request, url_for, flash
from flask_login import current_user, login_user, logout_user, login_required
from monolith.auth import current_user
from monolith.database import db, Reservation, RestaurantTable, User, ReservationState
from monolith.views.reservations import prettytime
from monolith.classes.customer_reservations import get_user_reservations, delete_reservation, update_reservation
from monolith.forms import ReservationForm

from datetime import datetime

customer_reservations = Blueprint('customer_reservations',
                                  __name__,
                                  url_prefix='/my_reservations')


@customer_reservations.route('/', methods=('GET', ))
@login_required
def get_reservations():
    form = ReservationForm()
    reservations = get_user_reservations(current_user.id)
    return render_template("customer_reservations.html",
                           reservations=reservations, form=form)


@customer_reservations.route('/<reservation_id>/update',
                             methods=(
                                 'POST',
                             ))
@login_required
def update_user_reservation(reservation_id: int):
    reservation = db.session.query(Reservation).filter_by(
        id=reservation_id).first()
    #form = ReservationForm()
    if (request.method == 'POST'):
        if ReservationForm(request.form).validate_on_submit():
            new_date = datetime.combine(ReservationForm(request.form).data['reservation_date'],
                                        ReservationForm(request.form).data['reservation_time'])
            new_seats = ReservationForm(request.form).data['seats']
            existing_reservation = db.session.query(Reservation).filter_by(
                user_id=current_user.id).filter_by(
                    restaurant_id=reservation.restaurant_id).filter_by(
                        reservation_time=new_date).filter_by(
                            seats=new_seats).first()
            print(existing_reservation)
            if (existing_reservation != None):
                flash(
                    f'You have already performed a reservation for the same time and seats at { reservation.restaurant.name }',
                    'reservation_mod')
                return redirect('/my_reservations/')
            else:
                if (update_reservation(reservation=reservation,
                                       new_reservation_time=new_date,
                                       new_seats=new_seats)):
                    flash('Your reservation has been correctly updated',
                          'reservation_mod')
                    return redirect('/my_reservations/')
                else:
                    flash(
                        'Overbooking Notification: your reservation has not been updated because of overbooking in the chosen date and time. Please, try another one.',
                        'reservation_mod')
                    return redirect('/my_reservations/')


@customer_reservations.route('/<reservation_id>/delete',
                             methods=(
                                 'GET',
                                 'DELETE',
                             ))
@login_required
def delete_user_reservation(reservation_id: int):
    if (delete_reservation(reservation_id=reservation_id)):
        flash('Your reservation has been correctly deleted', 'reservation_mod')
        return redirect(request.referrer)
    else:
        return render_template(
            "error.html",
            error_message="You are trying to delete an unexisting reservation."
        )
