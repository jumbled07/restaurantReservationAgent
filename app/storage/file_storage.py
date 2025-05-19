import json
import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

class FileStorage:
    def __init__(self):
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        
        # Initialize data files
        self.restaurants_file = self.data_dir / "restaurants.json"
        self.users_file = self.data_dir / "users.json"
        self.reservations_file = self.data_dir / "reservations.json"
        
        # Create files if they don't exist
        for file in [self.restaurants_file, self.users_file, self.reservations_file]:
            if not file.exists():
                logger.info(f"Creating new data file: {file}")
                file.write_text(json.dumps([]))

    def _read_json(self, file_path: Path) -> List[Dict]:
        try:
            logger.debug(f"Reading from {file_path}")
            content = file_path.read_text()
            if not content.strip():
                logger.warning(f"Empty file: {file_path}")
                return []
            return json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON from {file_path}: {str(e)}")
            logger.error(f"File content: {content}")
            raise ValueError(f"Invalid JSON in {file_path}: {str(e)}")
        except Exception as e:
            logger.error(f"Error reading {file_path}: {str(e)}")
            raise

    def _write_json(self, file_path: Path, data: List[Dict]):
        try:
            logger.debug(f"Writing to {file_path}")
            file_path.write_text(json.dumps(data, indent=2))
        except Exception as e:
            logger.error(f"Error writing to {file_path}: {str(e)}")
            raise

    # Restaurant operations
    def get_restaurants(self, filters: Optional[Dict] = None) -> List[Dict]:
        restaurants = self._read_json(self.restaurants_file)
        if not filters:
            return restaurants
            
        filtered = restaurants
        if "cuisine" in filters:
            filtered = [r for r in filtered if r["cuisine"].lower() == filters["cuisine"].lower()]
        if "location" in filters:
            filtered = [r for r in filtered if r["location"].lower() == filters["location"].lower()]
        if "price_range" in filters:
            filtered = [r for r in filtered if r["price_range"] == filters["price_range"]]
        return filtered

    def get_restaurant(self, restaurant_id: int) -> Optional[Dict]:
        restaurants = self._read_json(self.restaurants_file)
        return next((r for r in restaurants if r["id"] == restaurant_id), None)

    def add_restaurant(self, restaurant_data: Dict) -> Dict:
        restaurants = self._read_json(self.restaurants_file)
        restaurant_id = max([r["id"] for r in restaurants], default=0) + 1
        restaurant = {
            "id": restaurant_id,
            **restaurant_data,
            "created_at": datetime.utcnow().isoformat()
        }
        restaurants.append(restaurant)
        self._write_json(self.restaurants_file, restaurants)
        return restaurant

    # User operations
    def get_users(self) -> List[Dict]:
        return self._read_json(self.users_file)

    def get_user(self, user_id: int) -> Optional[Dict]:
        users = self._read_json(self.users_file)
        return next((u for u in users if u["id"] == user_id), None)

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        try:
            users = self._read_json(self.users_file)
            for user in users:
                if user.get("email") == email:
                    return user
            return None
        except Exception as e:
            logger.error(f"Error getting user by email: {str(e)}")
            raise

    def add_user(self, user_data: Dict) -> Dict:
        """Add a new user to storage"""
        try:
            logger.info(f"Adding new user: {user_data}")
            users = self._read_json(self.users_file)
            
            # Validate required fields
            required_fields = ["name", "email", "phone"]
            for field in required_fields:
                if field not in user_data:
                    raise ValueError(f"Missing required field: {field}")
            
            # Generate new user ID
            user_id = max([u["id"] for u in users], default=0) + 1
            
            # Create user record
            user = {
                "id": user_id,
                **user_data,
                "created_at": datetime.utcnow().isoformat()
            }
            
            # Validate preferences if present
            if "preferences" in user_data:
                if not isinstance(user_data["preferences"], dict):
                    raise ValueError("preferences must be a dictionary")
                if "cuisine" in user_data["preferences"] and not isinstance(user_data["preferences"]["cuisine"], list):
                    raise ValueError("preferences.cuisine must be a list")
            
            users.append(user)
            self._write_json(self.users_file, users)
            logger.info(f"Successfully added user with ID {user_id}")
            return user
        except Exception as e:
            logger.error(f"Error adding user: {str(e)}", exc_info=True)
            raise

    # Reservation operations
    def get_reservations(self, filters: Optional[Dict] = None) -> List[Dict]:
        reservations = self._read_json(self.reservations_file)
        if not filters:
            return reservations
            
        filtered = reservations
        if "user_id" in filters:
            filtered = [r for r in filtered if r["user_id"] == filters["user_id"]]
        if "restaurant_id" in filters:
            filtered = [r for r in filtered if r["restaurant_id"] == filters["restaurant_id"]]
        if "status" in filters:
            filtered = [r for r in filtered if r["status"] == filters["status"]]
        return filtered

    def get_reservation(self, reservation_id: int) -> Optional[Dict]:
        reservations = self._read_json(self.reservations_file)
        return next((r for r in reservations if r["id"] == reservation_id), None)

    def add_reservation(self, reservation_data: Dict) -> Dict:
        reservations = self._read_json(self.reservations_file)
        reservation_id = max([r["id"] for r in reservations], default=0) + 1
        reservation = {
            "id": reservation_id,
            **reservation_data,
            "status": "confirmed",
            "created_at": datetime.utcnow().isoformat()
        }
        reservations.append(reservation)
        self._write_json(self.reservations_file, reservations)
        return reservation

    def update_reservation(self, reservation_id: int, update_data: Dict) -> Optional[Dict]:
        reservations = self._read_json(self.reservations_file)
        for i, reservation in enumerate(reservations):
            if reservation["id"] == reservation_id:
                reservations[i] = {**reservation, **update_data}
                self._write_json(self.reservations_file, reservations)
                return reservations[i]
        return None

    def delete_reservation(self, reservation_id: int) -> bool:
        reservations = self._read_json(self.reservations_file)
        initial_length = len(reservations)
        reservations = [r for r in reservations if r["id"] != reservation_id]
        if len(reservations) < initial_length:
            self._write_json(self.reservations_file, reservations)
            return True
        return False 