import csv
from truckfinder import create_app, db
from truckfinder.models import FoodTruck
from seeds import data_path

app = create_app()

def seed_food_trucks():
    # This is needed to use the db methods
    with app.app_context():
        # Opens the food_truck csv file
        # newline="" corrects the csv handling
        with open(data_path("food_trucks.csv"), newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            items = []
            #Turns it into a dictionary of items, and then adds it to the DB
            items = [
                FoodTruck(
                    name=row["name"],
                    cuisine=row["cuisine"],
                    latitude=float(row["latitude"]),
                    longitude=float(row["longitude"]),
                    description=row["description"],
                    is_hidden=True if row["is_hidden"] == "True" else False
            )
                # This loops through every CSV row, and skips every empty row
                for row in reader
                if row["name"]
            ]

            # This stages all the objects for insertion
            db.session.bulk_save_objects(items)
            # Commits to the db so it saves
            db.session.commit()

            print("Data imported successfully!")
