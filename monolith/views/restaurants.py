from flask import Blueprint, redirect, render_template, request
from monolith.database import db, Restaurant, Like, Reservation, RestaurantTable
from monolith.auth import admin_required, current_user
from flask_login import (current_user, login_user, logout_user, login_required)
from monolith.forms import UserForm, ReservationForm
from sqlalchemy import func

restaurants = Blueprint('restaurants', __name__)


@restaurants.route('/restaurants')
def _restaurants(message=''):
    allrestaurants = db.session.query(Restaurant)
    return render_template("restaurants.html",
                           message=message,
                           restaurants=allrestaurants,
                           base_url="http://127.0.0.1:5000/restaurants")


@restaurants.route('/restaurants/<restaurant_id>')
def restaurant_sheet(restaurant_id):
    record = db.session.query(Restaurant).filter_by(
        id=int(restaurant_id)).all()[0]
    return render_template("restaurantsheet.html",
                           name=record.name,
                           likes=record.likes,
                           lat=record.lat,
                           lon=record.lon,
                           phone=record.phone)


@restaurants.route('/restaurants/reserve/<restaurant_id>',
                   methods=['GET', 'POST'])
def _reserve(restaurant_id):
    form = ReservationForm()
    record = db.session.query(Restaurant).filter_by(
        id=int(restaurant_id)).all()[0]

    if (request.method == 'POST'):
        if ReservationForm(request.form).validate_on_submit():
            #Retrieve sum of seats of the tables associated to a restaurant ( == Restaurant Capacity)
            restaurant_capacity = db.session.query(
                func.sum(RestaurantTable.seats)).filter_by(
                    restaurant_id=restaurant_id).first()[0]
            if restaurant_capacity is None:
                restaurant_capacity = 0

            print(restaurant_capacity)
            #Retrieve sum of currently reserved tables
            reserved_seats = db.session.query(func.sum(
                Reservation.seats)).filter_by(
                    restaurant_id=restaurant_id).filter_by(
                        reservation_date=ReservationForm(
                            request.form).data['reservation_date']).first()[0]
            if (reserved_seats is None):
                reserved_seats = 0

            print(reserved_seats)

            if ((reserved_seats + ReservationForm(request.form).data['seats'])
                    > restaurant_capacity):
                print('Overbooking')
                return _restaurants(
                    message=
                    'Overbooking Notification: the number of requested seats is not available'
                )

            subquery = db.session.query(Reservation.table_no).filter_by(
                reservation_date=ReservationForm(
                    request.form).data['reservation_date']).filter_by(
                        restaurant_id=restaurant_id).filter_by(
                            seats=ReservationForm(request.form).data['seats'])
            available_tables = db.session.query(RestaurantTable).filter_by(
                restaurant_id=restaurant_id).filter_by(
                    seats=ReservationForm(request.form).data['seats']).filter(
                        RestaurantTable.table_id.notin_(subquery))
            print(available_tables.all())
            if (available_tables.first() != None):
                reservation = Reservation()
                reservation.user_id = current_user.id
                reservation.restaurant_id = restaurant_id
                reservation.reservation_date = ReservationForm(
                    request.form).data['reservation_date']
                reservation.reservation_time = ReservationForm(
                    request.form).data['reservation_time']
                reservation.seats = ReservationForm(request.form).data['seats']
                reservation.table_no = available_tables.first().table_id
                db.session.add(reservation)
                db.session.commit()
                return _restaurants(message='Booking confirmed')
            else:
                return _restaurants(
                    message=
                    'No tables with the needed number of seats available in the selected day'
                )

    return render_template('reserve.html', name=record.name, form=form)


@restaurants.route('/restaurants/like/<restaurant_id>')
@login_required
def _like(restaurant_id):
    q = Like.query.filter_by(liker_id=current_user.id,
                             restaurant_id=restaurant_id)
    if q.first() != None:
        new_like = Like()
        new_like.liker_id = current_user.id
        new_like.restaurant_id = restaurant_id
        db.session.add(new_like)
        db.session.commit()
        message = ''
    else:
        message = 'You\'ve already liked this place!'
    return _restaurants(message)
