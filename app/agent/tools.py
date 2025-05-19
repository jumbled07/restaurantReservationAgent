from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from ..storage.file_storage import FileStorage
from .recommender import RestaurantRecommender

class Tool:
    def __init__(self, name: str, description: str, func: callable):
        self.name = name
        self.description = description
        self.func = func

class ToolRegistry:
    def __init__(self):
        self.storage = FileStorage()
        self.recommender = RestaurantRecommender()
        self.tools = self._initialize_tools()

    def _initialize_tools(self) -> Dict[str, Tool]:
        return {
            "search_restaurants": Tool(
                name="search_restaurants",
                description="Search for restaurants based on criteria like cuisine, location, price range",
                func=self._search_restaurants
            ),
            "get_restaurant_details": Tool(
                name="get_restaurant_details",
                description="Get detailed information about a specific restaurant",
                func=self._get_restaurant_details
            ),
            "check_availability": Tool(
                name="check_availability",
                description="Check table availability for a specific restaurant and time",
                func=self._check_availability
            ),
            "make_reservation": Tool(
                name="make_reservation",
                description="Make a reservation at a restaurant",
                func=self._make_reservation
            ),
            "get_recommendations": Tool(
                name="get_recommendations",
                description="Get restaurant recommendations based on user preferences",
                func=self._get_recommendations
            ),
            "cancel_reservation": Tool(
                name="cancel_reservation",
                description="Cancel an existing reservation",
                func=self._cancel_reservation
            ),
            "get_user_reservations": Tool(
                name="get_user_reservations",
                description="Get all reservations for a user",
                func=self._get_user_reservations
            ),
            "update_user_preferences": Tool(
                name="update_user_preferences",
                description="Update user preferences for better recommendations",
                func=self._update_user_preferences
            )
        }

    def _search_restaurants(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Search restaurants based on criteria"""
        restaurants = self.storage.get_restaurants()
        filtered = restaurants

        if "cuisine" in parameters:
            filtered = [r for r in filtered if r["cuisine"].lower() == parameters["cuisine"].lower()]
        if "location" in parameters:
            filtered = [r for r in filtered if r["location"].lower() == parameters["location"].lower()]
        if "price_range" in parameters:
            filtered = [r for r in filtered if r["price_range"] == parameters["price_range"]]
        if "features" in parameters:
            features = set(parameters["features"])
            filtered = [r for r in filtered if features.issubset(r["features"])]

        return {
            "status": "success",
            "data": {
                "restaurants": filtered[:10]  # Limit to 10 results
            }
        }

    def _get_restaurant_details(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed information about a specific restaurant"""
        restaurant_id = parameters.get("restaurant_id")
        if not restaurant_id:
            return {"status": "error", "message": "restaurant_id is required"}

        restaurant = self.storage.get_restaurant(restaurant_id)
        if not restaurant:
            return {"status": "error", "message": "Restaurant not found"}

        return {
            "status": "success",
            "data": restaurant
        }

    def _check_availability(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Check table availability for a specific restaurant and time"""
        restaurant_id = parameters.get("restaurant_id")
        date = parameters.get("date")
        party_size = parameters.get("party_size", 2)
        time = parameters.get("time")

        if not all([restaurant_id, date, time]):
            return {"status": "error", "message": "restaurant_id, date, and time are required"}

        try:
            requested_time = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        except ValueError:
            return {"status": "error", "message": "Invalid date or time format"}

        restaurant = self.storage.get_restaurant(restaurant_id)
        if not restaurant:
            return {"status": "error", "message": "Restaurant not found"}

        # Get existing reservations for the time slot
        reservations = self.storage.get_reservations()
        time_slot_reservations = [
            r for r in reservations
            if r["restaurant_id"] == restaurant_id
            and r["date"] == date
            and r["time"] == time
        ]

        # Calculate available capacity
        total_reserved = sum(r["party_size"] for r in time_slot_reservations)
        available_capacity = restaurant["capacity"] - total_reserved

        return {
            "status": "success",
            "data": {
                "available": available_capacity >= party_size,
                "available_capacity": available_capacity,
                "restaurant_capacity": restaurant["capacity"]
            }
        }

    def _make_reservation(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Make a reservation at a restaurant"""
        required_fields = ["restaurant_id", "user_id", "date", "time", "party_size"]
        if not all(field in parameters for field in required_fields):
            return {"status": "error", "message": f"Missing required fields: {required_fields}"}

        # Check availability first
        availability = self._check_availability(parameters)
        if availability["status"] == "error" or not availability["data"]["available"]:
            return availability

        # Create reservation
        reservation = {
            "restaurant_id": parameters["restaurant_id"],
            "user_id": parameters["user_id"],
            "date": parameters["date"],
            "time": parameters["time"],
            "party_size": parameters["party_size"],
            "status": "confirmed",
            "special_requests": parameters.get("special_requests", ""),
            "created_at": datetime.now().isoformat()
        }

        try:
            reservation_id = self.storage.add_reservation(reservation)
            return {
                "status": "success",
                "data": {
                    "reservation_id": reservation_id,
                    "reservation": reservation
                }
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _get_recommendations(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Get restaurant recommendations based on user preferences"""
        user_id = parameters.get("user_id")
        preferences = parameters.get("preferences", {})

        recommendations = self.recommender.get_recommendations(
            user_id=user_id,
            cuisine_preference=preferences.get("cuisine"),
            location=preferences.get("location"),
            price_range=preferences.get("price_range"),
            occasion=preferences.get("occasion")
        )

        return {
            "status": "success",
            "data": {
                "recommendations": recommendations
            }
        }

    def _cancel_reservation(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Cancel an existing reservation"""
        reservation_id = parameters.get("reservation_id")
        if not reservation_id:
            return {"status": "error", "message": "reservation_id is required"}

        try:
            self.storage.update_reservation(reservation_id, {"status": "cancelled"})
            return {"status": "success", "message": "Reservation cancelled successfully"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _get_user_reservations(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Get all reservations for a user"""
        user_id = parameters.get("user_id")
        if not user_id:
            return {"status": "error", "message": "user_id is required"}

        reservations = self.storage.get_reservations()
        user_reservations = [
            r for r in reservations
            if r["user_id"] == user_id
            and r["status"] != "cancelled"
        ]

        # Add restaurant details to each reservation
        for reservation in user_reservations:
            restaurant = self.storage.get_restaurant(reservation["restaurant_id"])
            if restaurant:
                reservation["restaurant"] = restaurant

        return {
            "status": "success",
            "data": {
                "reservations": user_reservations
            }
        }

    def _update_user_preferences(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Update user preferences for better recommendations"""
        user_id = parameters.get("user_id")
        preferences = parameters.get("preferences", {})
        
        if not user_id:
            return {"status": "error", "message": "user_id is required"}

        try:
            user = self.storage.get_user(user_id)
            if not user:
                return {"status": "error", "message": "User not found"}

            user["preferences"] = preferences
            self.storage.update_user(user_id, user)
            return {"status": "success", "message": "Preferences updated successfully"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool by name with given parameters"""
        if tool_name not in self.tools:
            return {"status": "error", "message": f"Tool {tool_name} not found"}
        
        try:
            return self.tools[tool_name].func(parameters)
        except Exception as e:
            return {"status": "error", "message": str(e)} 