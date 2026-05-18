import os
import uuid
from flask import Blueprint, render_template, url_for, request, redirect, jsonify, current_app
from werkzeug.utils import secure_filename
from truckfinder import db
from truckfinder.models import FoodTruck, MenuItem, FoodTruckHours, TruckRating, SubmittedTruck, TruckReview
from datetime import datetime
from truckfinder.forms import FoodTruckForm
from sqlalchemy.orm import selectinload
from sqlalchemy import func

"""
David Liberatore
5/8/2026
This stuff is needed in order to convert the data into a zip file
"""
from flask import Response
import io
import zipfile

from truckfinder.export import (
    export_foodtrucks_to_csv,
    export_menuitems_to_csv,
    export_hours_to_csv
)
# Author: Andre Nunes da Silva @ 05/02/26
# Optional image attachments on reviews. Limit to common web image formats and
# cap size at ~5MB so users can't blow up the static folder with huge uploads.
REVIEW_IMAGE_EXTS = {"png", "jpg", "jpeg", "gif", "webp"}
REVIEW_IMAGE_MAX_BYTES = 5 * 1024 * 1024
REVIEW_IMAGE_SUBPATH = os.path.join("uploads", "reviews")


def _review_image_dir():
    return os.path.join(current_app.static_folder, "uploads", "reviews")


def _save_review_image(file_storage, truck_id, user_id):
    # Returns the public URL (under /static) for the saved image, or None if no
    # file was attached. Raises ValueError on validation issues so the caller
    # can return a 400 with a user-facing message.
    if not file_storage or not file_storage.filename:
        return None

    original = secure_filename(file_storage.filename)
    ext = original.rsplit(".", 1)[-1].lower() if "." in original else ""
    if ext not in REVIEW_IMAGE_EXTS:
        raise ValueError("Unsupported image type. Use PNG, JPG, GIF, or WEBP.")

    file_storage.stream.seek(0, os.SEEK_END)
    size = file_storage.stream.tell()
    file_storage.stream.seek(0)
    if size > REVIEW_IMAGE_MAX_BYTES:
        raise ValueError("Image is too large (max 5MB).")

    upload_dir = _review_image_dir()
    os.makedirs(upload_dir, exist_ok=True)
    filename = f"{truck_id}_{user_id}_{uuid.uuid4().hex}.{ext}"
    file_storage.save(os.path.join(upload_dir, filename))
    return url_for("static", filename=f"uploads/reviews/{filename}")


def _delete_review_image(image_url):
    if not image_url:
        return
    # image_url looks like "/static/uploads/reviews/<file>" — strip the static
    # prefix so we can resolve it against the configured static_folder.
    prefix = "/static/"
    if not image_url.startswith(prefix):
        return
    rel = image_url[len(prefix):]
    path = os.path.join(current_app.static_folder, rel)
    if os.path.isfile(path):
        try:
            os.remove(path)
        except OSError:
            pass

bp = Blueprint('main', __name__)
# These routes connect to each html page, to make the path
# simpler and more professional than html files
@bp.route("/")
def home():
    return render_template("home.html", title="Home")

@bp.route("/stats/api", methods=["GET"])
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

@bp.route('/map')
def map_page():
    return render_template('Map.html', title="Map")

@bp.route('/about')
def about():
    return render_template('About.html', title="About")

# Andre Nunes da Silva : New route for user guide. 05/10/26
@bp.route('/guide')
def guide():
    return render_template('userGuide.html', title="User Guide")

@bp.route("/userForm", methods=["GET", "POST"])
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

# This is just for development stages
# Gets rid of all submissions
@bp.route("/reset_submissions")
def reset_submissions():
    SubmittedTruck.query.delete()
    db.session.commit()
    return "Submitted trucks reset!"

# This route is used as a helper route
# This is only called by the JavaScript in the main page
# It uses this rout to basically query all the truck data
@bp.route("/api/food_trucks")
def get_food_trucks():
    # This gets the time that it currently is
    now = datetime.now()
    # This gets the day that it is
    # This is important because in the DB you have all days saved as numbers
    today = now.weekday()

    # This line gets all the trucks in the db
    trucks = (
        FoodTruck.query
        .options(selectinload(FoodTruck.hours))
        .filter_by(is_hidden=False)
        .all()
    )
    # Makes a list to store this data
    data = []

    # Simple for - loop that goes through
    for truck in trucks:
        all_hours = sorted(
            truck.hours,
            key=lambda h: h.day_of_week
        )

        # This finds teh hours row for today from all the hours for this truck
        # Doesn't stop iterating throughout the hours until it finds today
        # After it finds today, it sets today's hours
        today_hours = next(
            (h for h in all_hours if h.day_of_week == today),
            None
        )
        # This uses the function at the bottom of the page
        # Sees if the truck is actually open
        is_open = is_truck_open(today_hours, now)

        # This appends all the data,
        # It puts it into separate dictionaries
        data.append({
            "id": truck.id,
            "name": truck.name,
            "latitude": truck.latitude,
            "longitude": truck.longitude,
            "description": truck.description,
            "is_open":is_open,
            # This makes a dictionary of each truck's hours
            "hours": [
                {
                    "day_of_week": h.day_of_week,
                    # %I tells the program to convert into the 12 - hour clock
                    # %M is the minutes
                    # %p says either AM or PM
                    "open_time": h.open_time.strftime("%I:%M %p").lstrip("0"),
                    "close_time": h.close_time.strftime("%I:%M %p").lstrip("0"),
                }
                for h in all_hours
            ]
        })

    # Jsonify is a function that converts the dictionaries into a separate JSON file
    # This is so the FE can interact with it
    # Jsonify however does not make a new file, and is only made over the browser
    # After it is made the program instantly forgets it after it is used
    return jsonify(data)
# David Liberatore
# 5/1/2026
# These are the routes used for the admin pages
# This returns all the submitted trucks data
@bp.route("/api/submitted_trucks")
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
@bp.route("/api/food_trucks_admin")
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

# This route works similarly to the food_truck route
@bp.route("/api/trucks/<int:truck_id>/menu")
def get_truck_menu(truck_id):
    # This gets the food truck with the specific menu
    # Saves this data into a variable
    items = MenuItem.query.filter_by(
        food_truck_id=truck_id
    ).all()
    # Makes blank list
    data = []
    # Loops through all items belonging to the truck
    for item in items:
        # Appends appropriate data
        data.append({
            "id": item.id,
            "name": item.name,
            "price": item.price,
        })
    # Returns a JSON version of the data
    return jsonify(data)

def is_truck_open(hours_row, now=None):
    # This handles if the truck has no hours for that day
    if not hours_row:
        return False

    # If not doesn't have a value, just make now = to the date now
    # And now contains the year, month, day, hour, etc
    if not now:
        now = datetime.now()

    # This then gives you the hours of now
    # It doesn't care about the date, it only cares about the hours
    current_time = now.time()

    # These pull from the table row
    # open_time and close_time are both row columns in the DB
    open_time = hours_row.open_time
    close_time = hours_row.close_time

    # Same - day hours
    # This returns a boolean if the truck opens later the same day
    if open_time < close_time:
        return open_time <= current_time <= close_time

    # Overnight hours (ex. 22:00 -> 2:40)
    # This returns a boolean if the truck opens overnight
    return current_time >= open_time or current_time <= close_time


@bp.route('/api/trucks/<int:truck_id>/rating', methods=['GET'])
def get_truck_rating(truck_id):
    ratings = TruckRating.query.filter_by(truck_id=truck_id).all()
    total, avg = db.session.query(
        func.count(TruckRating.id),
        func.avg(TruckRating.stars)
    ).filter(TruckRating.truck_id == truck_id).first()

    avg = round(avg or 0, 2)
    total = total or 0

    return jsonify({ "avg_rating": avg, "total_ratings": total })

@bp.route('/api/trucks/<int:truck_id>/rating', methods=['POST'])
def post_truck_rating(truck_id):
    body    = request.get_json()
    user_id = body.get("user_id")
    stars   = int(body.get("stars", 0))
    if not user_id or not (1 <= stars <= 5):
        return jsonify({"error": "Invalid payload"}), 400
    existing = TruckRating.query.filter_by(truck_id=truck_id, user_id=user_id).first()
    old_stars = existing.stars if existing else None
    if existing:
        existing.stars = stars
        existing.updated_at = datetime.utcnow()
    else:
        db.session.add(TruckRating(truck_id=truck_id, user_id=user_id, stars=stars))
    db.session.commit()
    print(f"[RATING] truck={truck_id} user={user_id} old={old_stars} new={stars}")
    all_ratings = TruckRating.query.filter_by(truck_id=truck_id).all()
    total = len(all_ratings)
    avg = round(sum(r.stars for r in all_ratings) / total, 2)
    return jsonify({ "avg_rating": avg, "total_ratings": total })

@bp.route('/api/trucks/<int:truck_id>/rating/delete', methods=['POST'])
def delete_truck_rating(truck_id):
    body = request.get_json()
    user_id = body.get("user_id")
    existing = TruckRating.query.filter_by(truck_id=truck_id, user_id=user_id).first()
    if existing:
        db.session.delete(existing)
        db.session.commit()
    all_ratings = TruckRating.query.filter_by(truck_id=truck_id).all()
    total = len(all_ratings)
    avg = round(sum(r.stars for r in all_ratings) / total, 2) if total > 0 else 0
    return jsonify({ "avg_rating": avg, "total_ratings": total })

# Review Routes | Author : Andre Nunes da Silva @ 04/20/26

# Same map page, but pre-loads a specific truck's reviews in an overlay
@bp.route('/map/reviews/<int:truck_id>')
def map_with_reviews(truck_id):
    return render_template('Map.html', title="Map", open_reviews_for=truck_id)

@bp.route('/api/trucks/<int:truck_id>/reviews', methods=['GET']) # This method returns all reviews, for a given truck
def get_truck_reviews(truck_id):
    reviews = TruckReview.query.filter_by(truck_id=truck_id)\
        .order_by(TruckReview.created_at.desc()).all()

    ratings_data = dict(
        db.session.query(TruckRating.user_id, TruckRating.stars)
        .filter(TruckRating.truck_id == truck_id)
        .all()
    )

    # Author: Andre Nunes da Silva @ 04/20/26
    # Added stars to the review payload so the FE can actually display the user's star rating next to their review.
    # Was using ratings_data above but forgot to pipe it through, which made every review show 0 stars on the panel.
    data = [{
        "id": r.id,
        "user_id": r.user_id,
        "display_name": r.display_name or "Anonymous",
        "review_text": r.review_text,
        "stars": ratings_data.get(r.user_id, 0),
        "image_url": r.image_url,
        "created_at": r.created_at.isoformat() if r.created_at else None
    } for r in reviews]
    return jsonify({"reviews": data, "total": len(data)})

# POST TRUCK REVIEWS

@bp.route('/api/trucks/<int:truck_id>/review', methods=['POST']) # after it gets, it uses the first route, when it hits post (when a user sends a review, it uses this route)

def post_truck_review(truck_id):
    # Author: Andre Nunes da Silva @ 05/02/26
    # Accept either JSON (legacy / no image) or multipart/form-data (when an
    # image is attached). The frontend always uses FormData now, but keeping
    # JSON support means we don't break any direct API callers.
    if request.content_type and request.content_type.startswith("multipart/form-data"):
        user_id = request.form.get("user_id")
        review_text = (request.form.get("review_text") or "").strip()
        display_name = (request.form.get("display_name") or "").strip() or None
        image_file = request.files.get("image")
    else:
        body = request.get_json() or {}
        user_id = body.get('user_id')
        review_text = (body.get('review_text') or "").strip()
        display_name = (body.get('display_name') or "").strip() or None
        image_file = None

    if not user_id or not review_text:
        return jsonify({"error": "user_id and review_text are REQUIRED"}), 400
    if len(review_text) > 1000:
        return jsonify({"error": "Review is too long, maximum 1000 characters."}), 400

    try:
        new_image_url = _save_review_image(image_file, truck_id, user_id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    existing = TruckReview.query.filter_by(truck_id=truck_id, user_id=user_id).first()
    if existing:
        existing.review_text = review_text
        existing.display_name = display_name
        # If a new image was attached, replace the old one on disk so we don't
        # leak orphaned files. If no new image, keep the existing one.
        if new_image_url:
            _delete_review_image(existing.image_url)
            existing.image_url = new_image_url
    else:
        db.session.add(TruckReview(
            truck_id=truck_id,
            user_id=user_id,
            review_text=review_text,
            display_name=display_name,
            image_url=new_image_url
        ))
    db.session.commit()
    return jsonify({"success": True})

# Delete, also grabs post
@bp.route('/api/trucks/<int:truck_id>/review/delete', methods=['POST'])
def delete_truck_review(truck_id):
    body = request.get_json() or {}
    user_id = body.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400
    existing = TruckReview.query.filter_by(truck_id=truck_id, user_id=user_id).first()
    if existing:
        _delete_review_image(existing.image_url)
        db.session.delete(existing)
        db.session.commit()
    return jsonify({"success": True})
"""
David Liberatore
5/8/2026
This route is used to let the user download our gathered data
"""
@bp.route("/download/food-truck-data")
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