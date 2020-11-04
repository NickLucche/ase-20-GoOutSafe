from flask_login.utils import login_required
from monolith.classes.exceptions import DatabaseError, FormValidationError, GoOutSafeError
from monolith.classes.user import edit_user_data, new_operator, new_user, users_view
from flask import Blueprint, redirect, render_template, flash, request
from flask_login import login_user
from monolith.database import Restaurant, db, User
from monolith.auth import admin_required, current_user
from monolith.forms import OperatorForm, UserForm, UserProfileEditForm

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
            login_user(u)
            return redirect('/')
        except FormValidationError:
            return render_template('create_user.html', form=form)
        except Exception as e:
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
            return render_template('create_user.html', form=form)
        except Exception as e:
            return render_template("error.html", error_message=str(e))

    return render_template('create_user.html', form=form)


@users.route('/users/edit/<user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if current_user.id != int(user_id):
        return render_template("error.html", error_message="You aren't supposed to be here!")

    form = UserProfileEditForm(obj=current_user)
    if request.method == 'POST':
        try:
            edit_user_data(form, user_id)
            return redirect('/users/edit/' + user_id)
        except GoOutSafeError:
            return render_template("useredit.html", form=form)
        except Exception as e:
            return render_template("error.html", error_message=str(e))
    return render_template("useredit.html", form=form)
