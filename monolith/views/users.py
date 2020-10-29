from monolith.classes.exceptions import DatabaseError, GoOutSafeError
from monolith.classes.user import new_operator, new_user, users_view
from flask import Blueprint, redirect, render_template, flash, request
from flask_login import login_user
from monolith.database import Restaurant, db, User
from monolith.auth import admin_required
from monolith.forms import OperatorForm, UserForm

users = Blueprint('users', __name__)

@users.route('/users')
def _users():
    users = users_view()
    return render_template("users.html", users=users)


@users.route('/create_user', methods=['GET', 'POST'])
def create_user():
    form = UserForm()
    if request.method == 'POST':
        try:
            u = new_user(form)
            flash("User successfully created! Logging in.")
            login_user(u)
            return redirect('/')
        except GoOutSafeError as e:
            return render_template("error.html", error_message=str(e))
            
    return render_template('create_user.html', form=form)


@users.route('/create_operator', methods=['GET', 'POST'])
def create_operator():
    form = OperatorForm()
    if request.method == 'POST':
        try:
            u = new_operator(form)
            flash("User successfully created! Logging in.")
            login_user(u)
            return redirect('/')
        except GoOutSafeError as e:
            return render_template("error.html", error_message=str(e))

    return render_template('create_user.html', form=form)