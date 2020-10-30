from flask import Blueprint, redirect, render_template, request
from sqlalchemy import func
from monolith.database import db, User
from monolith.auth import admin_required
from monolith.forms import SearchUserForm
from monolith.classes.authority_frontend import mark_user

authority = Blueprint('authority', __name__)

@authority.route('/authority')
@admin_required
def _authority(message=''):
    return render_template("authority.html")

@authority.route('/authority/users')
@admin_required
def _authority_users(message=''):
    allusers = db.session.query(User)
    return render_template("users_for_authority.html", users=allusers)

@authority.route('/authority/search_user', methods=['GET', 'POST'])
@admin_required
def _search_user():
    form = SearchUserForm()
    if request.method == 'POST':

        if form.validate_on_submit():
            filter_user = User()
            form.populate_obj(filter_user)
            
            q = db.session.query(User)
            if filter_user.firstname != "":
                q = q.filter(func.lower(User.firstname) == func.lower(filter_user.firstname))
            if filter_user.lastname != "":
                q = q.filter(func.lower(User.lastname) == func.lower(filter_user.lastname))
            if filter_user.email != "":
                q = q.filter(func.lower(User.email) == func.lower(filter_user.email))
            return render_template("users_for_authority.html", users=q)

    return render_template('create_user.html', form=form)

@authority.route('/authority/mark/<marked_user_id>')
@admin_required
def _mark(marked_user_id):
    message = mark_user(marked_user_id)

    if message != '':
        return render_template("error.html", error_message=message)
    else:
        return redirect('/authority/users')
