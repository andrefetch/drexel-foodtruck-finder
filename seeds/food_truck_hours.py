import csv
from datetime import datetime
from truckfinder import create_app, db
from truckfinder.models import FoodTruckHours
from seeds import data_path

app = create_app()

def seed_food_truck_hours():
    # This is needed to use the db methods
    with app.app_context():
        # Opens the food_truck csv file
        # newline="" corrects the csv handling
        with open(data_path("food_truck_hours.csv"), newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            #Turns it into a dictionary of items, and then adds it to the DB
            items = [
                FoodTruckHours(
                    food_truck_id=int(row["food_truck_id"]),
                    day_of_week=int(row["day_of_week"]),
                    # This parses the time from a string
                    # Looks at value and sees %H as the hour
                    # Looks at value and sees %M as the minute
                    # Converts everything into numbers
                    open_time=datetime.strptime(row["open_time"].strip(), "%H:%M").time(),
                    close_time=datetime.strptime(row["close_time"].strip(), "%H:%M").time(),
            )
                # This loops through every CSV row, and skips every empty row
                for row in reader
                if row["food_truck_id"]
            ]

            # This stages all the objects for insertion
            db.session.bulk_save_objects(items)
            # Commits to the db so it saves
            db.session.commit()

            print("Hours seeded")
