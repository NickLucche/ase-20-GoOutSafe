from monolith.classes.exceptions import GoOutSafeError, UserNotInDB
from monolith.classes.authentication import authenticate_user
from flask import Blueprint, render_template, redirect, request
from flask_login import (current_user, login_user, logout_user,
                         login_required)

from monolith.database import db, User
from monolith.forms import LoginForm

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        try:
            authenticate_user(form)
            return redirect('/')
        except GoOutSafeError:
            form.email.errors.append("The email or password inserted is invalid")

    return render_template('login.html', form=form)


@auth.route("/logout")
def logout():
    logout_user()
    return redirect('/')
