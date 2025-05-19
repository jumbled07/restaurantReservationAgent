from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime
from ..agent.core import Agent
from ..storage.file_storage import FileStorage
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Restaurant Reservation API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
agent = Agent()
storage = FileStorage()

# Pydantic models for request/response validation
class ChatRequest(BaseModel):
    message: str
    user_info: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    response: str

class RestaurantBase(BaseModel):
    name: str
    cuisine: str
    location: str
    address: str
    capacity: int
    opening_time: str
    closing_time: str
    price_range: str
    rating: float
    features: Dict[str, bool]
    menu: Dict[str, List[Dict[str, Any]]]

class RestaurantCreate(RestaurantBase):
    pass

class Restaurant(RestaurantBase):
    id: int
    created_at: str

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    name: str
    email: str
    phone: str
    preferences: Optional[Dict[str, Any]] = None

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int
    created_at: str

    class Config:
        from_attributes = True

class ReservationBase(BaseModel):
    restaurant_id: int
    user_id: int
    date: str
    time: str
    party_size: int
    special_requests: Optional[str] = None

class ReservationCreate(ReservationBase):
    pass

class Reservation(ReservationBase):
    id: int
    status: str
    created_at: str

    class Config:
        from_attributes = True

# API endpoints
@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Process a chat message and return a response"""
    try:
        response = agent.process_message(request.message, request.user_info)
        return ChatResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Restaurant endpoints
@app.get("/api/v1/restaurants", response_model=List[Restaurant])
async def get_restaurants():
    """Get all restaurants"""
    return storage.get_restaurants()

@app.get("/api/v1/restaurants/{restaurant_id}", response_model=Restaurant)
async def get_restaurant(restaurant_id: int):
    """Get a specific restaurant by ID"""
    restaurant = storage.get_restaurant(restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return restaurant

@app.post("/api/v1/restaurants", response_model=Restaurant)
async def create_restaurant(restaurant: RestaurantCreate):
    """Create a new restaurant"""
    try:
        restaurant_id = storage.add_restaurant(restaurant.dict())
        return storage.get_restaurant(restaurant_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# User endpoints
@app.post("/api/v1/users", response_model=User)
async def create_user(user: UserCreate):
    """Create a new user"""
    try:
        logger.info(f"Attempting to create user with data: {user.dict()}")
        user_dict = user.dict()
        logger.info(f"Validated user data: {user_dict}")
        
        # Check if user with same email already exists
        existing_user = storage.get_user_by_email(user_dict["email"])
        if existing_user:
            logger.warning(f"User with email {user_dict['email']} already exists")
            raise HTTPException(status_code=400, detail="User with this email already exists")
        
        try:
            # Create user and return the created user directly
            created_user = storage.add_user(user_dict)
            logger.info(f"Successfully created user: {created_user}")
            return created_user
        except Exception as storage_error:
            logger.error(f"Error in storage operations: {str(storage_error)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Error storing user data: {str(storage_error)}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error creating user: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/v1/users/{user_id}", response_model=User)
async def get_user(user_id: int):
    """Get a specific user by ID"""
    user = storage.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/api/v1/users/email/{email}")
async def get_user_by_email(email: str):
    """Get user by email"""
    try:
        user = storage.get_user_by_email(email)
        if user:
            return user
        raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Reservation endpoints
@app.post("/api/v1/reservations", response_model=Reservation)
async def create_reservation(reservation: ReservationCreate):
    """Create a new reservation"""
    try:
        # Check if restaurant exists
        restaurant = storage.get_restaurant(reservation.restaurant_id)
        if not restaurant:
            raise HTTPException(status_code=404, detail="Restaurant not found")
        
        # Check if user exists
        user = storage.get_user(reservation.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Create reservation
        reservation_id = storage.add_reservation(reservation.dict())
        return storage.get_reservation(reservation_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/v1/reservations/{reservation_id}", response_model=Reservation)
async def get_reservation(reservation_id: int):
    """Get a specific reservation by ID"""
    reservation = storage.get_reservation(reservation_id)
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    return reservation

@app.get("/api/v1/users/{user_id}/reservations", response_model=List[Reservation])
async def get_user_reservations(user_id: int):
    """Get all reservations for a user"""
    # Check if user exists
    user = storage.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    reservations = storage.get_reservations()
    return [r for r in reservations if r["user_id"] == user_id]

@app.put("/api/v1/reservations/{reservation_id}", response_model=Reservation)
async def update_reservation(reservation_id: int, updates: Dict[str, Any]):
    """Update a reservation"""
    try:
        storage.update_reservation(reservation_id, updates)
        return storage.get_reservation(reservation_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/api/v1/reservations/{reservation_id}")
async def cancel_reservation(reservation_id: int):
    """Cancel a reservation"""
    try:
        storage.update_reservation(reservation_id, {"status": "cancelled"})
        return {"message": "Reservation cancelled successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 