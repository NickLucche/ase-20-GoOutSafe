from flask import Blueprint, redirect, render_template, current_app, url_for

from monolith.database import db, Restaurant
from monolith.auth import current_user
from monolith.classes.notification_retrieval import fetch_notifications

home = Blueprint('home', __name__)


@home.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for("auth.login"))
    if current_user is not None and hasattr(current_user, 'id'):
        if hasattr(current_user, 'is_admin') and current_user.is_admin == True:
            return redirect("/authority")
        restaurants = db.session.query(Restaurant)
        notifs = fetch_notifications(current_app, current_user, unread_only=True)
    else:
        restaurants = []
        notifs = []
    return render_template("index.html", restaurants=restaurants, notifications=notifs)


@home.route('/signup')
def signup():
    return render_template("signup.html")