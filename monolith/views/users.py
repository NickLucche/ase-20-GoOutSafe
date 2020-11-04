from monolith.classes.exceptions import DatabaseError, GoOutSafeError, FormValidationError
from monolith.classes.user import new_operator, new_user, users_view, edit_user_data
from flask import Blueprint, redirect, render_template, flash, request, current_app
from flask_login import login_user, login_required
from monolith.database import Restaurant, db, User
from monolith.auth import admin_required, current_user
from monolith.forms import OperatorForm, UserForm, UserProfileEditForm
from monolith.classes.notification_retrieval import *


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


@users.route('/notifications', methods=['GET'])
@login_required
def all_notifications():
    try:
        if hasattr(current_user, 'is_admin') and current_user.is_admin == True:
            # redirect authority to another page
            return redirect("/authority")
        notifs = fetch_notifications(current_app, current_user, unread_only=False)
        return render_template('notifications_list.html', notifications_list=notifs, message='You were in contact with a positive user in the following occasions:')
    except GoOutSafeError as e:
        return render_template("error.html", error_message=str(e))

@users.route('/notifications/<notification_id>', methods=['GET'])
@login_required
def get_notification(notification_id):
    # show notification detail view and mark notification as seen
    try:
        notification = Notification.query.filter_by(id=notification_id).join(Restaurant).with_entities(Notification, Restaurant).first()
        if notification[0].notification_checked == False:
            notification[0].notification_checked = True
            db.session.commit()
        notif = notification[0]
        notif.restaurant = notification[1]
        return render_template('notification_detail.html', notification=notif)
    except GoOutSafeError as e:
        return render_template("error.html", error_message=str(e))
