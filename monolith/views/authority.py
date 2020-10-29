from flask import Blueprint, redirect, render_template, request
from sqlalchemy import func
from monolith.database import db, User
from monolith.auth import admin_required
from monolith.forms import SearchUserForm
from monolith.background import register_positive

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
    user = User.query.filter_by(id=marked_user_id).first()
    if user == None:
        message = 'Error! Unable to mark the user. User not found'
    elif user.is_positive == False:
        user.is_positive = True
        db.session.commit()
        message = ''
        register_positive(marked_user_id)
    else:
        message = 'You\'ve already marked this user as positive!'

    if message != '':
        return render_template("error.html", error_message=message)
    else:
        return redirect('/authority/users')