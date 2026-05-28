#Created by Alex Troeschel, 5/28/2026
#Built off of seed.py, created by David Liberatore
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

        #Gets user input as 'r', 'w', or 'rw' to decide whether to update csv from db, update db from csv, or both
        user_input = None

        while not user_input:
            user_input = input("Do you want to read (update csv), write (update db), or both ('r', 'w', or 'rw' respectively)?\n").lower()
            if user_input not in "rw":
                user_input = None
                print("Error: User Input wasn't 'r', 'w', or 'rw'. Please try again.")
        read_write = user_input
        user_input = None

        #If the user wants to update csv, takes up to four choices to choose what csv files to update
        if "r" in read_write:
            options = ["submitted_trucks", "truck_ratings", "truck_reviews", "food_trucks"]
            chosen = []

            #The loop runs until options are exhausted or the user types 'exit'
            while len(options) > 0 and user_input != "exit":
                print("Which tables do you want to read (push to csv)?", end="\n(")

                for item in options:

                    if item == "submitted_trucks":
                        print("'s' for user submissions", end=", ")

                    elif item == "truck_ratings":
                        print("'r' for ratings", end=", ")

                    elif item == "truck_reviews":
                        print("'e' for reviews", end=", ")

                    else:
                        print("'t' for trucks", end=", ")
                user_input = input("'a' for all, and 'exit' to stop)\n").lower()


                if user_input == "a":
                    chosen = ["submitted_trucks", "truck_ratings", "truck_reviews", "food_trucks"]
                    options = []

                elif user_input == "s":

                    if "submitted_trucks" in options:
                        options.remove("submitted_trucks")
                        chosen.append("submitted_trucks")

                    else:
                        print("Option is already chosen. Please choose again.")

                elif user_input == "r":

                    if "truck_ratings" in options:
                        options.remove("truck_ratings")
                        chosen.append("truck_ratings")

                    else:
                        print("Option is already chosen. Please choose again.")
                
                elif user_input == "e":

                    if "truck_reviews" in options:
                        options.remove("truck_reviews")
                        chosen.append("truck_reviews")
                        
                    else:
                        print("Option is already chosen. Please choose again.")
                
                elif user_input == "t":

                    if "food_trucks" in options:
                        options.remove("food_trucks")
                        chosen.append("food_trucks")
                        
                    else:
                        print("Option is already chosen. Please choose again.")
            write_csv(chosen)
        
        if "w" in read_write:
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
        print("Seeding successful!")