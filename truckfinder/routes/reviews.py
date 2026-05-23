from flask import Blueprint, url_for, current_app, jsonify, request, render_template
from datetime import datetime
import os
import uuid
from werkzeug.utils import secure_filename
from truckfinder.models import TruckRating, TruckReview
from truckfinder import db
from sqlalchemy import func


reviews_bp = Blueprint("reviews", __name__)

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

@reviews_bp.route('/api/trucks/<int:truck_id>/rating', methods=['GET'])
def get_truck_rating(truck_id):
    total, avg = db.session.query(
        func.count(TruckRating.id),
        func.avg(TruckRating.stars)
    ).filter(TruckRating.truck_id == truck_id).first()

    avg = round(avg or 0, 2)
    total = total or 0

    return jsonify({ "avg_rating": avg, "total_ratings": total })

@reviews_bp.route('/api/trucks/<int:truck_id>/rating', methods=['POST'])
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
    total, avg = db.session.query(
        func.count(TruckRating.id),
        func.avg(TruckRating.stars)
    ).filter(TruckRating.truck_id == truck_id).first()
    avg = round(avg or 0, 2)
    total = total or 0
    return jsonify({ "avg_rating": avg, "total_ratings": total })

@reviews_bp.route('/api/trucks/<int:truck_id>/rating/delete', methods=['POST'])
def delete_truck_rating(truck_id):
    body = request.get_json()
    user_id = body.get("user_id")
    existing = TruckRating.query.filter_by(truck_id=truck_id, user_id=user_id).first()
    if existing:
        db.session.delete(existing)
        db.session.commit()
    total, avg = db.session.query(
        func.count(TruckRating.id),
        func.avg(TruckRating.stars)
    ).filter(TruckRating.truck_id == truck_id).first()
    avg = round(avg or 0, 2)
    total = total or 0
    return jsonify({ "avg_rating": avg, "total_ratings": total })

# Review Routes | Author : Andre Nunes da Silva @ 04/20/26

# Same map page, but pre-loads a specific truck's reviews in an overlay
@reviews_bp.route('/map/reviews/<int:truck_id>')
def map_with_reviews(truck_id):
    return render_template('Map.html', title="Map", open_reviews_for=truck_id)

@reviews_bp.route('/api/trucks/<int:truck_id>/reviews', methods=['GET']) # This method returns all reviews, for a given truck
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

@reviews_bp.route('/api/trucks/<int:truck_id>/review', methods=['POST']) # after it gets, it uses the first route, when it hits post (when a user sends a review, it uses this route)
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
@reviews_bp.route('/api/trucks/<int:truck_id>/review/delete', methods=['POST'])
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

