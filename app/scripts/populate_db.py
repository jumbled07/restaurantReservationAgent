from ..storage.file_storage import FileStorage

# Sample restaurant data
RESTAURANTS = [
    {
        "name": "La Bella Italia",
        "cuisine": "Italian",
        "location": "Downtown",
        "address": "123 Main St",
        "capacity": 80,
        "opening_time": "11:00",
        "closing_time": "23:00",
        "price_range": "$$$",
        "rating": 4.5,
        "features": {
            "parking": True,
            "outdoor_seating": True,
            "bar": True,
            "private_rooms": True
        },
        "menu": {
            "appetizers": [
                {"name": "Bruschetta", "price": 12},
                {"name": "Caprese Salad", "price": 14}
            ],
            "main_courses": [
                {"name": "Spaghetti Carbonara", "price": 22},
                {"name": "Margherita Pizza", "price": 18}
            ]
        }
    },
    {
        "name": "Sakura Japanese",
        "cuisine": "Japanese",
        "location": "Midtown",
        "address": "456 Oak Ave",
        "capacity": 60,
        "opening_time": "12:00",
        "closing_time": "22:00",
        "price_range": "$$$$",
        "rating": 4.8,
        "features": {
            "parking": True,
            "sushi_bar": True,
            "private_rooms": True
        },
        "menu": {
            "sushi": [
                {"name": "Dragon Roll", "price": 18},
                {"name": "Salmon Nigiri", "price": 8}
            ],
            "main_courses": [
                {"name": "Teriyaki Chicken", "price": 24},
                {"name": "Ramen", "price": 16}
            ]
        }
    },
    {
        "name": "Spice Garden",
        "cuisine": "Indian",
        "location": "Uptown",
        "address": "789 Spice Lane",
        "capacity": 100,
        "opening_time": "11:30",
        "closing_time": "22:30",
        "price_range": "$$",
        "rating": 4.6,
        "features": {
            "parking": True,
            "buffet": True,
            "private_rooms": True,
            "catering": True
        },
        "menu": {
            "appetizers": [
                {"name": "Samosa", "price": 8},
                {"name": "Pakora", "price": 9}
            ],
            "main_courses": [
                {"name": "Butter Chicken", "price": 20},
                {"name": "Vegetable Biryani", "price": 18}
            ]
        }
    }
]

def populate_storage():
    storage = FileStorage()
    
    try:
        # Add restaurants
        for restaurant_data in RESTAURANTS:
            storage.add_restaurant(restaurant_data)
        
        print("Storage populated successfully!")
        
    except Exception as e:
        print(f"Error populating storage: {str(e)}")

if __name__ == "__main__":
    populate_storage() 