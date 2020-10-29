from logging import error
from flask import Blueprint, redirect, render_template, request, flash
from monolith.database import db, Restaurant, Like, RestaurantTable
from monolith.auth import admin_required, current_user
from flask_login import (current_user, login_user, logout_user,
                         login_required)
from monolith.forms import RestaurantProfileEditForm

restaurants = Blueprint('restaurants', __name__)

@restaurants.route('/restaurants')
def _restaurants(message=''):
    allrestaurants = db.session.query(Restaurant)
    return render_template("restaurants.html", message=message, restaurants=allrestaurants, base_url="http://127.0.0.1:5000/restaurants")

@restaurants.route('/restaurants/<restaurant_id>')
def restaurant_sheet(restaurant_id):
    record = Restaurant.query.get(restaurant_id)
    if not record:
        return render_template("error.html", error_message="The page you're looking does not exists")
    return render_template("restaurantsheet.html", name=record.name, likes=record.likes, lat=record.lat, lon=record.lon, phone=record.phone)

@restaurants.route('/restaurants/like/<restaurant_id>')
@login_required
def _like(restaurant_id):
    r = Restaurant.query.get(restaurant_id)
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
    return _restaurants(message)

@restaurants.route('/restaurants/edit/<restaurant_id>', methods=['GET', 'POST'])
@login_required
def _edit(restaurant_id):
    if (not current_user.restaurant_id) or current_user.restaurant_id != int(restaurant_id):
        return render_template("error.html", error_message="You haven't the permissions to access this page")
    r = Restaurant.query.get(restaurant_id)
    tables = RestaurantTable.query.filter_by(restaurant_id = restaurant_id).order_by(RestaurantTable.table_id.asc())
    form = RestaurantProfileEditForm(obj=r)
    
    if request.method == 'POST':
        if form.validate_on_submit():
            flash("Infos saved successfully")
            for t in tables:
                RestaurantTable.query.filter_by(restaurant_id = t.restaurant_id, table_id = t.table_id).delete()
            db.session.commit()
            i = 1
            while request.form.get('table_' + str(i)) != None:
                new_table = RestaurantTable()
                new_table.restaurant_id = restaurant_id
                new_table.table_id = i
                new_table.seats = request.form.get('table_' + str(i))
                db.session.add(new_table)
                i += 1
            db.session.commit()
            return redirect('/restaurants/edit/' + restaurant_id)
    return render_template("restaurantedit.html", restaurant=r, form=form, tables=tables)