import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_admin import Admin
from flask_login import LoginManager
from flask_admin.contrib.sqla import ModelView
from flask_babel import Babel

db = SQLAlchemy()
# Makes Login Manager
login_manager = LoginManager()

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

# import AFTER db/login_manager exist
from truckfinder.admin_views import MyAdminIndexView, SecureModelView

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///site.db')

    # Everything the app writes at runtime (exported CSVs, review photos) lives
    # under WRITABLE_DIR. Serverless hosts (Vercel) mount the code read-only and
    # only allow writes under /tmp, so they set WRITABLE_DIR. When it is unset we
    # keep writing to the in-repo locations that local and Railway deploys use.
    writable_dir = os.environ.get('WRITABLE_DIR')
    if writable_dir:
        app.config['EXPORT_DIR'] = os.path.join(writable_dir, 'data')
        app.config['REVIEW_UPLOAD_DIR'] = os.path.join(writable_dir, 'uploads', 'reviews')
    else:
        app.config['EXPORT_DIR'] = os.path.join(BASE_DIR, 'data')
        app.config['REVIEW_UPLOAD_DIR'] = os.path.join(app.static_folder, 'uploads', 'reviews')

    babel = Babel(app)
    db.init_app(app)
    login_manager.init_app(app)
    Migrate(app, db)

    from truckfinder.models import FoodTruck, MenuItem, FoodTruckHours, SubmittedTruck, User

    admin = Admin(app, name="Admin Dashboard", index_view=MyAdminIndexView())

    # IMPORTANT: use SecureModelView (not ModelView)
    admin.add_view(SecureModelView(FoodTruck, db.session))
    admin.add_view(SecureModelView(MenuItem, db.session))
    admin.add_view(SecureModelView(FoodTruckHours, db.session))
    admin.add_view(SecureModelView(SubmittedTruck, db.session))

    from truckfinder.routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    from truckfinder.routes.pages import pages_bp
    from truckfinder.routes.api import api_bp
    from truckfinder.routes.reviews import reviews_bp
    from truckfinder.routes.admin import admin_bp
    from truckfinder.routes.exports import exports_bp

    app.register_blueprint(pages_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(reviews_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(exports_bp)

    return app
