from flask import Blueprint, render_template, redirect, url_for, jsonify
from truckfinder.models import SubmittedTruck, FoodTruck, MenuItem
from truckfinder import db
from sqlalchemy import func
from truckfinder.forms import FoodTruckForm

pages_bp = Blueprint("main", __name__)

@pages_bp.route("/")
def home():
    return render_template("home.html", title="Home")

@pages_bp.route('/map')
def map_page():
    return render_template('Map.html', title="Map")

@pages_bp.route('/about')
def about():
    return render_template('About.html', title="About")

# Andre Nunes da Silva : New route for user guide. 05/10/26
@pages_bp.route('/guide')
def guide():
    return render_template('userGuide.html', title="User Guide")

# Alex Troeschel : New route for system manual. 05/24/26
@pages_bp.route('/sysmanual')
def sysmanual():
    return render_template('systemManual.html', title="System Manual")

@pages_bp.route("/userForm", methods=["GET", "POST"])
def userForm():
    form = FoodTruckForm()

    if form.validate_on_submit():
        new_truck = SubmittedTruck(
            name=form.name.data,
            latitude=float(form.latitude.data),
            longitude=float(form.longitude.data)
        )

        db.session.add(new_truck)
        db.session.commit()

        return redirect(url_for("main.home"))

    return render_template("userForm.html", form=form)

@pages_bp.route("/stats/api", methods=["GET"])
def stats_api():
    truck_count = FoodTruck.query.filter_by(is_hidden=False).count()
    menu_item_count = MenuItem.query.count()
    cuisine_count = (
        db.session.query(func.count(func.distinct(FoodTruck.cuisine)))
        .filter(FoodTruck.is_hidden == False, FoodTruck.cuisine.isnot(None), FoodTruck.cuisine != "")
        .scalar()
    ) or 0
    return jsonify({
        "trucks": truck_count,
        "menu_items": menu_item_count,
        "cuisines": cuisine_count,
    })
