"""
David Liberatore
5/8/2026
This file is made to seed an admin file.
Only use this if you accidentally clear the db

python -m seeds.seed_admin
"""
from truckfinder import create_app, db
from truckfinder.models import User
from werkzeug.security import generate_password_hash

app = create_app()

def seed_admin():
    with app.app_context():

        if not User.query.filter_by(username="admin").first():

            user = User(
                username="admin",
                password_hash=generate_password_hash("password123"),
                is_admin=True
            )

            db.session.add(user)
            db.session.commit()

            print("Admin created")