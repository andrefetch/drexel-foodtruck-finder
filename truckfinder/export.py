"""
David Liberatore
5/8/2026
This file makes functions that allows the csv file to update from the admin page
The admin page information is now the main source of truth when it comes to the data
not the csv files it used to seed from in the early development stages
"""

import csv
from flask import current_app
from truckfinder import db
from truckfinder.models import FoodTruck, MenuItem, FoodTruckHours
import os


def export_path(filename):
    # Resolved per-request instead of at import time: on a read-only serverless
    # filesystem the directory only exists once we point it under /tmp, and
    # creating it at import would blow up before the app can even start.
    export_dir = current_app.config["EXPORT_DIR"]
    os.makedirs(export_dir, exist_ok=True)
    return os.path.join(export_dir, filename)


# -------------------------
# FOOD TRUCKS
# -------------------------
def export_foodtrucks_to_csv():
    path = export_path("food_trucks.csv")
    trucks = FoodTruck.query.all()

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["name","cuisine","latitude","longitude","description"])

        for t in trucks:
            writer.writerow([t.name,t.cuisine,t.latitude,t.longitude,t.description])


# -------------------------
# MENU ITEMS
# -------------------------
def export_menuitems_to_csv():
    path = export_path("menu_items.csv")
    items = MenuItem.query.all()

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "price", "food_truck_id"])

        for i in items:
            writer.writerow([i.name, f"{i.price:.2f}", i.food_truck_id])


# -------------------------
# HOURS
# -------------------------
def export_hours_to_csv():
    path = export_path("food_truck_hours.csv")
    hours = FoodTruckHours.query.all()

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["food_truck_id","day_of_week","open_time","close_time"])

        for h in hours:
            writer.writerow([h.food_truck_id,h.day_of_week,h.open_time,h.close_time])