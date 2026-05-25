from truckfinder import create_app, db
from seeds.food_trucks import seed_food_trucks
from seeds.menu_items import seed_menu_items
from seeds.food_truck_hours import seed_food_truck_hours
from seeds.seed_admin import seed_admin

app = create_app()

# This is only ran if seed.py is the main file
# This file is for updating our DB according to the csv file
if __name__ == "__main__":
    with app.app_context():
        print("Resetting database...")

        # Gets rid of all the data in the db so it has a fresh slate
        db.drop_all()
        # Remakes all of db
        db.create_all()

        # Calls both functions so it is both made in the db
        seed_food_trucks()
        seed_menu_items()
        seed_food_truck_hours()
        seed_admin()

        # Prints this message when done
        print("Database reset and seeded successfully!")