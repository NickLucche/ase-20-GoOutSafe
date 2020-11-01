from flask import Blueprint, redirect, render_template, current_app

from monolith.database import db, Restaurant, Like
from monolith.auth import current_user
from monolith.classes.notification_retrieval import fetch_notifications


home = Blueprint('home', __name__)


@home.route('/')
def index():
    if current_user is not None and hasattr(current_user, 'id'):
        if hasattr(current_user, 'is_admin') and current_user.is_admin == True:
            return redirect("/authority")
        restaurants = db.session.query(Restaurant)
        notifs = fetch_notifications(current_app, current_user)
    else:
        restaurants = []
        notifs = []
    return render_template("index.html", restaurants=restaurants, notifications=notifs)
