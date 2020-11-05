from logging import error
from monolith.classes.exceptions import GoOutSafeError
from monolith.classes.restaurant import add_review, edit_tables, update_review
import monolith.classes.customer_reservations as cr
from flask import Blueprint, redirect, render_template, request, flash
from monolith.database import Reservation, db, Restaurant, Review, RestaurantTable
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
                           restaurants=allrestaurants,
                           base_url='restaurants')


@restaurants.route('/restaurants/<restaurant_id>',
                   methods=['GET', 'POST'])
def restaurant_sheet(restaurant_id):
    record = Restaurant.query.get(restaurant_id)
    if not record:
        return render_template("error.html", error_message="The page you're looking does not exists")
    review = Review.query.filter_by(reviewer_id=current_user.id, restaurant_id=restaurant_id).scalar()
    if review is not None:
        # show the user their updated view
        update_review(record, review.stars)
    if current_user.is_authenticated and not current_user.restaurant_id \
        and review is None:
        # the user is logged and hasn't already a review for this restaurant
        form = RatingForm()
        if(request.method == 'POST'):
            if form.validate_on_submit():
                if form.review is not None:
                    add_review(current_user.id, restaurant_id, int(request.form.get("stars_number")), text=str(form.review.data))                                        
                else:
                    add_review(current_user.id, restaurant_id, int(request.form.get("stars_number")))
                # update review count immediately so user can see it
                record = update_review(record, int(request.form.get("stars_number")))
        else:
            return render_template("restaurantsheet.html", form=form, name=record.name, likes=record.likes, lat=record.lat, lon=record.lon, phone=record.phone, avg_stars=record.avg_stars, n_reviews=record.num_reviews)

    return render_template("restaurantsheet.html", name=record.name, likes=record.likes, lat=record.lat, lon=record.lon, phone=record.phone, avg_stars=record.avg_stars, n_reviews=record.num_reviews)


@restaurants.route('/restaurants/reserve/<restaurant_id>',
                   methods=['GET', 'POST'])
@login_required
def _reserve(restaurant_id):
    form = ReservationForm()
    record = db.session.query(Restaurant).filter_by(
        id=int(restaurant_id)).all()[0]

    if (request.method == 'POST'):
        if (current_user.is_positive):
            return render_template('error.html', error_message="Error: you cannot reserve a table while marked as positive!")
        reservation_time = datetime.combine(
                ReservationForm(request.form).data['reservation_date'],
                ReservationForm(request.form).data['reservation_time'])
        if (reservation_time <= datetime.now()):
            flash ('Invalid Date Error. You cannot reserve a table in the past!', 'booking')
            return redirect(request.referrer)
        if ReservationForm(request.form).validate_on_submit():
            reservation_time = datetime.combine(
                ReservationForm(request.form).data['reservation_date'],
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
                flash('Overbooking Notification: no tables with the wanted seats on the requested date and time. Please, try another one.', 'booking')
                return redirect('/restaurants')
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
                flash('Booking confirmed', 'booking')
                return redirect('/restaurants')

    return render_template('reserve.html', name=record.name, form=form)


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
            return render_template("restaurantedit.html", restaurant=r, form=form, tables=tables)


    tables = RestaurantTable.query.filter_by(restaurant_id = restaurant_id).order_by(RestaurantTable.table_id.asc())
    return render_template("restaurantedit.html", restaurant=r, form=form, tables=tables)