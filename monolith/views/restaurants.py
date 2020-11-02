from logging import error
from monolith.classes.exceptions import GoOutSafeError
from monolith.classes.restaurant import add_review, edit_tables
import monolith.classes.customer_reservations as cr
from flask import Blueprint, redirect, render_template, request, flash
from monolith.database import db, Restaurant, Review, RestaurantTable
from monolith.auth import admin_required, current_user
from flask_login import (current_user, login_user, logout_user,
                         login_required)
from monolith.forms import RatingForm, UserForm, ReservationForm, RestaurantProfileEditForm
from sqlalchemy import func
from datetime import datetime

restaurants = Blueprint('restaurants', __name__)


@restaurants.route('/restaurants')
def _restaurants(message=''):
    allrestaurants = db.session.query(Restaurant)
    return render_template("restaurants.html",
                           message=message,
                           restaurants=allrestaurants)


@restaurants.route('/restaurants/<restaurant_id>',
                   methods=['GET', 'POST'])
def restaurant_sheet(restaurant_id):
    record = Restaurant.query.get(restaurant_id)
    if not record:
        return render_template("error.html", error_message="The page you're looking does not exists")
    if current_user.is_authenticated and not current_user.restaurant_id \
        and Review.query.filter_by(reviewer_id=current_user.id, restaurant_id=restaurant_id).scalar() is None:
        # the user is logged and hasn't already a review for this restaurant
        form = RatingForm()
        if(request.method == 'POST'):
            if form.validate_on_submit():
                if form.review is not None:
                    add_review(current_user.id, restaurant_id, int(request.form.get("stars_number")), text=str(form.review.data))
                else:
                    add_review(current_user.id, restaurant_id, int(request.form.get("stars_number")))
        else:
            return render_template("restaurantsheet.html", form=form, name=record.name, likes=record.likes, lat=record.lat, lon=record.lon, phone=record.phone)

    return render_template("restaurantsheet.html", name=record.name, likes=record.likes, lat=record.lat, lon=record.lon, phone=record.phone)


@restaurants.route('/restaurants/reserve/<restaurant_id>',
                   methods=['GET', 'POST'])
def _reserve(restaurant_id):
    form = ReservationForm()
    record = db.session.query(Restaurant).filter_by(
        id=int(restaurant_id)).all()[0]

    if (request.method == 'POST'):
        if ReservationForm(request.form).validate_on_submit():
            reservation_time = datetime.combine(
                ReservationForm(request.form).data['reservation_time'],
                ReservationForm(request.form).data['reservation_time'])
            overlapping_tables = cr.get_overlapping_tables(
                restaurant_id=record.id,
                reservation_time=reservation_time,
                reservation_seats=ReservationForm(request.form).data['seats'],
                avg_stay_time=record.avg_stay_time)
            if (cr.is_overbooked(restaurant_id=record.id,
                                 reservation_seats=ReservationForm(
                                     request.form).data['seats'],
                                 overlapping_tables=overlapping_tables)):
                return _restaurants(
                    message=
                    'Overbooking Notification: no tables with the wanted seats on the requested date and time. Please, try another one.'
                )
            else:
                assigned_table = cr.assign_table_to_reservation(
                    overlapping_tables=overlapping_tables,
                    restaurant_id=record.id,
                    reservation_seats=ReservationForm(
                        request.form).data['seats'])
                reservation = Reservation(user_id=current_user.id,
                                          restaurant_id=record.id,
                                          reservation_time=reservation_time,
                                          seats=ReservationForm(
                                              request.form).data['seats'],
                                          table_no=assigned_table.table_id)
                cr.add_reservation(reservation)
                return _restaurants(message='Booking confirmed')

    return render_template('reserve.html', name=record.name, form=form)


@restaurants.route('/restaurants/like/<restaurant_id>')
@login_required
def _like(restaurant_id):
    """r = Restaurant.query.get(restaurant_id)
    if not r:
        return render_template("error.html", error_message="The page you're looking does not exists")
    q = Like.query.filter_by(liker_id=current_user.id, restaurant_id=restaurant_id)
    if q.first() != None:
        new_like = Like()
        new_like.liker_id = current_user.id
        new_like.restaurant_id = restaurant_id
        db.session.add(new_like)
        db.session.commit()
        message = ''
    else:
        message = 'You\'ve already liked this place!'
    return _restaurants(message)"""

@restaurants.route('/restaurants/edit/<restaurant_id>', methods=['GET', 'POST'])
@login_required
def _edit(restaurant_id):
    if (not current_user.restaurant_id) or current_user.restaurant_id != int(restaurant_id):
        return render_template("error.html", error_message="You haven't the permissions to access this page")
    r = Restaurant.query.get(restaurant_id)
    form = RestaurantProfileEditForm(obj=r)
    
    if request.method == 'POST':
        try:
            edit_tables(form, request.form, restaurant_id)
            flash("Infos saved successfully")            
            return redirect('/restaurants/edit/' + restaurant_id)
        except GoOutSafeError as e:
            return render_template("error.html", error_message=str(e))


    tables = RestaurantTable.query.filter_by(restaurant_id = restaurant_id).order_by(RestaurantTable.table_id.asc())
    return render_template("restaurantedit.html", restaurant=r, form=form, tables=tables)