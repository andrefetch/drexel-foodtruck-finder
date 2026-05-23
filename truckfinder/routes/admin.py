from flask import Blueprint, jsonify
from truckfinder.models import SubmittedTruck, FoodTruck

admin_bp = Blueprint("admin_api", __name__)

# David Liberatore
# 5/1/2026
# These are the routes used for the admin pages
# This returns all the submitted trucks data
@admin_bp.route("/api/submitted_trucks")
def get_submitted_trucks():
    trucks = SubmittedTruck.query.all()
    data = []
    for truck in trucks:
        data.append({
            "id": truck.id,
            "name": truck.name,
            "latitude": truck.latitude,
            "longitude": truck.longitude,
            "is_approved": truck.is_approved
        })
    # Returns as a json file
    return jsonify(data)

# Sees all the trucks in the main foodtrucks
@admin_bp.route("/api/food_trucks_admin")
def get_food_trucks_admin():
    trucks = FoodTruck.query.all()  # no is_hidden filter
    data = []
    for truck in trucks:
        data.append({
            "id": truck.id,
            "name": truck.name,
            "latitude": truck.latitude,
            "longitude": truck.longitude,
            "is_hidden": truck.is_hidden,
            "is_open": False  # simplified for admin view
        })
    return jsonify(data)
