from truckfinder import create_app, db
from seeds.food_trucks import seed_food_trucks
from seeds.menu_items import seed_menu_items
from seeds.food_truck_hours import seed_food_truck_hours
from seeds.seed_admin import seed_admin
from seeds.seed_prep import write_csv
from seeds.user_inputs import seed_submitted_trucks, seed_truck_ratings, seed_truck_reviews
app = create_app()

# This is only ran if seed.py is the main file
# This file is for updating our DB according to the csv file
if __name__ == "__main__":
    with app.app_context():
        print("Resetting database...")
        write_csv(['submitted_trucks', 'truck_ratings', 'truck_reviews'])
        # Gets rid of all the data in the db so it has a fresh slate
        db.drop_all()
        # Remakes all of db
        db.create_all()

        # Calls both functions so it is both made in the db
        seed_food_trucks()
        seed_menu_items()
        seed_food_truck_hours()
        seed_admin()
        seed_truck_reviews()
        seed_truck_ratings()
        seed_submitted_trucks()

        # Prints this message when done
        print("Database reset and seeded successfully!")