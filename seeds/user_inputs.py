#Created by Alex Troeschel 5/28/2026
#Built off of seeds/food_trucks.py, by David Liberatore
import csv
from truckfinder import create_app, db
from datetime import datetime, date
from truckfinder.models import SubmittedTruck, TruckRating, TruckReview
from seeds import data_path

app = create_app()

def seed_submitted_trucks():
    # This is needed to use the db methods
    with app.app_context():
        # Opens the food_truck csv file
        # newline="" corrects the csv handling
        with open(data_path("submitted_trucks.csv"), newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            #Turns it into a dictionary of items, and then adds it to the DB
            items = [
                SubmittedTruck(
                    id=int(row["id"]),
                    name=row["name"],
                    latitude=float(row["latitude"]),
                    longitude=float(row["longitude"]),
                    is_approved=True if row["is_approved"] == "True" else False,
                    merged=True if row["merged"] == "True" else False
            )
                # This loops through every CSV row, and skips every empty row
                for row in reader
                if row["id"]
            ]

            # This stages all the objects for insertion
            db.session.bulk_save_objects(items)
            # Commits to the db so it saves
            db.session.commit()

            print("Data imported successfully!")

def seed_truck_ratings():
    # This is needed to use the db methods
    with app.app_context():
        # Opens the food_truck csv file
        # newline="" corrects the csv handling
        with open(data_path("truck_ratings.csv"), newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            items = []
            #Turns it into a dictionary of items, and then adds it to the DB
            for row in reader:
                if row["id"]:
                    createDate = list(map(int, row["created_at"].split("-")))
                    updateDate = list(map(int, row["updated_at"].split("-")))

                    items.append(TruckRating(
                        id=int(row["id"]),
                        truck_id=int(row["truck_id"]),
                        user_id=row["user_id"],
                        stars=int(row["stars"]),
                        created_at=date(createDate[0], createDate[1], createDate[2]),
                        updated_at=date(updateDate[0], updateDate[1], updateDate[2])
                ))
            
            # This stages all the objects for insertion
            db.session.bulk_save_objects(items)
            # Commits to the db so it saves
            db.session.commit()

            print("Data imported successfully!")

def seed_truck_reviews():
    # This is needed to use the db methods
    with app.app_context():
        # Opens the food_truck csv file
        # newline="" corrects the csv handling
        with open(data_path("truck_reviews.csv"), newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            items = []
            for row in reader:
                if row["id"]:
                    rowDate = list(map(int, row["created_at"].split("-")))
                    #Turns it into a dictionary of items, and then adds it to the DB
                    items.append(TruckReview(
                            id=int(row["id"]),
                            truck_id=int(row["truck_id"]),
                            user_id=row["user_id"],
                            review_text=row["review_text"],
                            display_name=row["display_name"],
                            image_url=row["image_url"],
                            created_at=date(rowDate[0], rowDate[1], rowDate[2])
                    ))

            # This stages all the objects for insertion
            db.session.bulk_save_objects(items)
            # Commits to the db so it saves
            db.session.commit()

            print("Data imported successfully!")