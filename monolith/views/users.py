from flask import Blueprint, redirect, render_template, request
from flask_login import login_user
from monolith.database import Restaurant, db, User
from monolith.auth import admin_required
from monolith.forms import OperatorForm, UserForm

users = Blueprint('users', __name__)

@users.route('/users')
def _users():
    users = db.session.query(User)
    return render_template("users.html", users=users)


@users.route('/create_user', methods=['GET', 'POST'])
def create_user():
    form = UserForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            if User.query.filter_by(email = form.email) != None:
                # user with same email already exists
                return render_template("error.html", error_message="An user with the same email already exists!")
            new_user = User()
            form.populate_obj(new_user)
            new_user.set_password(form.password.data) #pw should be hashed with some salt
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect('/')

    return render_template('create_user.html', form=form)


@users.route('/create_operator', methods=['GET', 'POST'])
def create_operator():
    form = OperatorForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            if User.query.filter_by(email = form.email) != None:
                # user with same email already exists
                return render_template("error.html", error_message="An user with the same email already exists!")
            new_user = User()
            new_restaurant = Restaurant()
            form.populate_obj(new_user)
            form.populate_obj(new_restaurant)
            new_user.set_password(form.password.data) #pw should be hashed with some salt
            new_user.is_operator = True
            db.session.add(new_restaurant)
            db.session.flush()
            new_user.restaurant_id = new_restaurant.id
            db.session.add(new_user)
            
            db.session.commit()
            login_user(new_user)
            return redirect('/')

    return render_template('create_user.html', form=form)