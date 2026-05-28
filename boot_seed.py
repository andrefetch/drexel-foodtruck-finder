# Andre Nunes da Silva : 05/28/26

from truckfinder import create_app, db
from seeds.food_trucks import seed_food_trucks
from seeds.menu_items import seed_menu_items
from seeds.food_truck_hours import seed_food_truck_hours
from seeds.seed_admin import seed_admin
from seeds.user_inputs import seed_submitted_trucks, seed_truck_ratings, seed_truck_reviews

app = create_app()

# reseeds on every deployement, since railway processes sqlite as empheral data I can't change it without 
# migrating to a new database. this is the method I use for now which works.
if __name__ == "__main__":
    with app.app_context():
        print("Seeding database...")
        db.drop_all()
        db.create_all()

        seed_food_trucks()
        seed_menu_items()
        seed_food_truck_hours()
        seed_admin()
        seed_truck_reviews()
        seed_truck_ratings()
        seed_submitted_trucks()

        print("Database seeded successfully!")
