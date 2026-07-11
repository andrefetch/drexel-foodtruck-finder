import csv
from truckfinder import db
from truckfinder.models import MenuItem
from seeds import data_path

def seed_menu_items():
    # Opens the menu items csv and makes it the reader
    with open(data_path("menu_items.csv"), newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        # Turns it into a dictionary and then adds it to the db
        items = [
            MenuItem(
                name=row["name"],
                price=float(row["price"]),
                food_truck_id=int(row["food_truck_id"])
            )
            for row in reader
            if row['name']
        ]

        # Then commits so it saves
        db.session.bulk_save_objects(items)
        db.session.commit()

        print("Menu items seeded")