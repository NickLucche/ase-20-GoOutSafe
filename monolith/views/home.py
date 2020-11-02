from flask import Blueprint, redirect, render_template

from monolith.database import db, Restaurant
from monolith.auth import current_user


home = Blueprint('home', __name__)


@home.route('/')
def index():
    if current_user is not None and hasattr(current_user, 'id'):
        if hasattr(current_user, 'is_admin') and current_user.is_admin == True:
            return redirect("/authority")
        restaurants = db.session.query(Restaurant)
    else:
        restaurants = None
    return render_template("index.html", restaurants=restaurants)
