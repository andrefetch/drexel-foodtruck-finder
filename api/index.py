import os

os.environ.setdefault("DATABASE_URL", "sqlite:////tmp/truckfinder/site.db")
os.environ.setdefault("WRITABLE_DIR", "/tmp/truckfinder")

os.makedirs("/tmp/truckfinder", exist_ok=True)

from truckfinder import create_app, db
from truckfinder.models import FoodTruck

_VERCEL_PREFIX = "/api/index"


class _StripVercelPrefix:
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        path = environ.get("PATH_INFO", "")
        if path == _VERCEL_PREFIX or path.startswith(_VERCEL_PREFIX + "/"):
            environ["PATH_INFO"] = path[len(_VERCEL_PREFIX):] or "/"
        return self.wsgi_app(environ, start_response)


app = create_app()
app.wsgi_app = _StripVercelPrefix(app.wsgi_app)


def _seed_on_cold_start():
    # Importing the seed modules builds their own app objects, so it is done
    # lazily, inside the context, rather than at module import.
    from seeds.food_trucks import seed_food_trucks
    from seeds.menu_items import seed_menu_items
    from seeds.food_truck_hours import seed_food_truck_hours
    from seeds.seed_admin import seed_admin
    from seeds.user_inputs import (
        seed_submitted_trucks,
        seed_truck_ratings,
        seed_truck_reviews,
    )

    with app.app_context():
        db.create_all()

        # A warm instance keeps /tmp between requests, so only seed a fresh one.
        if FoodTruck.query.first():
            return

        print("Cold start: seeding /tmp database...")
        seed_food_trucks()
        seed_menu_items()
        seed_food_truck_hours()
        seed_admin()
        seed_truck_reviews()
        seed_truck_ratings()
        seed_submitted_trucks()
        print("Database seeded successfully!")


_seed_on_cold_start()
