from monolith.classes.exceptions import DatabaseError, GoOutSafeError
from monolith.classes.user import new_operator, new_user, users_view
from flask import Blueprint, redirect, render_template, flash, request, current_app
from flask_login import login_user, login_required
from monolith.database import Restaurant, db, User
from monolith.auth import admin_required
from monolith.forms import OperatorForm, UserForm
from monolith.classes.notification_retrieval import *
from monolith.auth import current_user


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

@users.route('/notifications', methods=['GET'])
@login_required
def all_notifications():
    try:
        if hasattr(current_user, 'is_admin') and current_user.is_admin == True:
            # redirect authority to another page
            return redirect("/authority")
        notifs = fetch_notifications(current_app, current_user)
        return render_template('notifications_list.html', notifications=notifs, message='You were in contact with a positive user in the following occasions:')
    except GoOutSafeError as e:
        return render_template("error.html", error_message=str(e))

@users.route('/notifications/<notification_id>', methods=['GET'])
@login_required
def get_notification(notification_id):
    # show notification detail view and mark notification as seen
    try:
        notification = Notification.query.join(Restaurant).filter_by(id=notification_id).with_entities(Notification, Restaurant).first()
        if notification[0].notification_checked == False:
            notification[0].notification_checked = True
            db.session.commit()
        notif = notification[0].to_dict()
        notif['restaurant'] = notification[1]
        render_template('notification_detail.html', notification=notif)
    except GoOutSafeError as e:
        return render_template("error.html", error_message=str(e))

    

    