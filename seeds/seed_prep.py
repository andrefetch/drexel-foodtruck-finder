#Created by Alex Troeschel, 5/28/2026
from truckfinder import create_app, db
from truckfinder.models import SubmittedTruck, TruckRating, TruckReview, FoodTruck
import csv
from datetime import datetime, date
from seeds import data_path
app = create_app()

def write_csv(choice = ['submitted_trucks', 'truck_ratings', 'truck_reviews', 'food_trucks']):
    with app.app_context():
        if 'submitted_trucks' in choice:
            with open(data_path('submitted_trucks.csv'), 'w', newline='', encoding='utf-8') as csvsubtrucks:
                fieldnames = ['id', 'name', 'latitude', 'longitude', 'is_approved', 'merged']
                writer = csv.DictWriter(csvsubtrucks, fieldnames=fieldnames)
                
                writer.writeheader()
                submitted = SubmittedTruck.query.all()
                for sub in submitted:
                    writer.writerow({'id': sub.id,
                                    'name': sub.name,
                                    'latitude': sub.latitude,
                                    'longitude': sub.longitude,
                                    'is_approved': sub.is_approved,
                                    'merged': sub.merged})
        
        if 'truck_ratings' in choice:
            with open(data_path('truck_ratings.csv'), 'w', newline='', encoding='utf-8') as csvsubtrucks:
                fieldnames = ['id', 'truck_id', 'user_id', 'stars', 'created_at', 'updated_at']
                writer = csv.DictWriter(csvsubtrucks, fieldnames=fieldnames)
                
                writer.writeheader()
                submitted = TruckRating.query.all()
                for sub in submitted:
                    writer.writerow({'id': sub.id,
                                    'truck_id': sub.truck_id,
                                    'user_id': sub.user_id,
                                    'stars': sub.stars,
                                    'created_at': sub.created_at.date(),
                                    'updated_at': sub.updated_at.date()})
        
        if 'truck_reviews' in choice:
            with open(data_path('truck_reviews.csv'), 'w', newline='', encoding='utf-8') as csvsubtrucks:
                fieldnames = ['id', 'truck_id', 'user_id', 'review_text', 'display_name', 'image_url', 'created_at']
                writer = csv.DictWriter(csvsubtrucks, fieldnames=fieldnames)
                
                writer.writeheader()
                submitted = TruckReview.query.all()
                for sub in submitted:
                    writer.writerow({'id': sub.id,
                                    'truck_id': sub.truck_id,
                                    'user_id': sub.user_id,
                                    'review_text': sub.review_text,
                                    'display_name': sub.display_name,
                                    'image_url': sub.image_url,
                                    'created_at': sub.created_at.date()})
        
        if 'food_trucks' in choice:
            with open(data_path('food_trucks.csv'), 'w', newline='', encoding='utf-8') as csvsubtrucks:
                fieldnames = ['name', 'cuisine', 'latitude', 'longitude', 'description', 'is_hidden']
                writer = csv.DictWriter(csvsubtrucks, fieldnames=fieldnames)
                
                writer.writeheader()
                submitted = FoodTruck.query.all()
                for sub in submitted:
                    writer.writerow({'name': sub.name,
                                    'cuisine': sub.cuisine,
                                    'latitude': sub.latitude,
                                    'longitude': sub.longitude,
                                    'description': sub.description,
                                    'is_hidden': sub.is_hidden})
        print("Chosen files written to csv")