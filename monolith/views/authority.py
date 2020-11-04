from flask import Blueprint, redirect, render_template, request
from monolith.database import db, User
from monolith.auth import admin_required
from monolith.forms import SearchUserForm
from monolith.classes.authority_frontend import mark_user, search_user, INCUBATION_PERIOD_COVID

authority = Blueprint('authority', __name__)

@authority.route('/authority')
@admin_required
def _authority(message=''):
    return render_template("authority.html")

@authority.route('/authority/search_user', methods=['GET', 'POST'])
@admin_required
def _search_user(message=''):
    form = SearchUserForm()
    if request.method == 'POST':

        if form.validate_on_submit():
            filter_user = User()
            form.populate_obj(filter_user)
            user, error_message = search_user(filter_user)
            if user == None:
                return render_template("error.html", error_message=error_message)
            else:
                return render_template("single_user_for_authority.html", user=user)

    return render_template('create_user.html', form=form)

@authority.route('/authority/mark/<marked_user_id>')
@admin_required
def _mark(marked_user_id):
    message, user = mark_user(marked_user_id)

    if message != '':
        return render_template("error.html", error_message=message)
    else:
        return render_template("single_user_for_authority.html", user=user)

@authority.route('/authority/trace_contacts/<user_id>')
@admin_required
def _get_contact_list(user_id):
    from monolith.classes.notifications import contact_tracing_users, check_visited_places

    exec_chain = (check_visited_places.s(user_id, INCUBATION_PERIOD_COVID) | contact_tracing_users.s(user_id))()
    users_at_risk = exec_chain.get()
    
    return render_template("users_for_authority.html", users=users_at_risk)
    