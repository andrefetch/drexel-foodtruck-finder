"""
David Liberatore
5/8/2026
This authorizes users to login
"""

from flask import Blueprint, redirect, url_for, render_template
from flask_login import login_user
from werkzeug.security import check_password_hash
from truckfinder.forms import LoginForm
from truckfinder import login_manager
from truckfinder.models import User

auth_bp = Blueprint("auth", __name__)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    form = LoginForm()

    # Checks if the username and password matches up with the real user and password
    if form.validate_on_submit():

        user = User.query.filter_by(
            username=form.username.data
        ).first()

        if user and check_password_hash(
            user.password_hash,
            form.password.data
        ):
            login_user(user)
            return redirect(url_for("admin.index"))

    return render_template("login.html", form=form)
