"""
David Liberatore
5/8/2026
This stuff is needed in order to convert the data into a zip file
"""
from flask import Response
import io
import zipfile
from flask import Blueprint

from truckfinder.export import (
    export_foodtrucks_to_csv,
    export_menuitems_to_csv,
    export_hours_to_csv
)

exports_bp = Blueprint("exports", __name__)

"""
David Liberatore
5/8/2026
This route is used to let the user download our gathered data
"""
@exports_bp.route("/download/food-truck-data")
def download_all_csvs():

    # 1. Generate latest CSV files first
    export_foodtrucks_to_csv()
    export_menuitems_to_csv()
    export_hours_to_csv()

    # 2. Create in-memory ZIP
    memory_file = io.BytesIO()

    # 3. Makes the zip file with each csv for hours, trucks, and menu items
    with zipfile.ZipFile(memory_file, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write("data/food_trucks.csv", arcname="foodtrucks.csv")
        zf.write("data/menu_items.csv", arcname="menu_items.csv")
        zf.write("data/food_truck_hours.csv", arcname="hours.csv")

    memory_file.seek(0)

    # Returns a zip file that the user can download
    return Response(
        memory_file.getvalue(),
        mimetype="application/zip",
        headers={
            "Content-Disposition": "attachment; filename=food_truck_data.zip"
        }
    )