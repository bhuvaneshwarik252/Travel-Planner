from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List, Any, Dict

# Shared properties
class UserBase(BaseModel):
    name: str
    email: EmailStr

# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str

# Properties to receive via API on update (all optional)
class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

# Properties to return to client
class UserResponse(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    user_name: str

class TokenData(BaseModel):
    email: Optional[str] = None

class TripBase(BaseModel):
    destination: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    itinerary: Any # JSON string or List/Dict

class TripCreate(TripBase):
    pass

class TripResponse(TripBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# --- Travel Planner Schemas ---

class Coordinates(BaseModel):
    latitude: float
    longitude: float

class DestinationDetails(BaseModel):
    name: str
    country: str
    region: Optional[str] = None
    population: Optional[int] = None
    timezone: Optional[str] = None
    coordinates: Coordinates
    # Additional info
    wikiDataId: Optional[str] = None

class Attraction(BaseModel):
    name: str
    kind: str
    description: Optional[str] = None
    image: Optional[str] = None
    wikipedia_url: Optional[str] = None
    coordinates: Optional[Coordinates] = None

class FlightOffer(BaseModel):
    price: str
    currency: str
    airline: str
    departure: str
    arrival: str
    duration: Optional[str] = None

class Activity(BaseModel):
    """Individual activity within a day's itinerary"""
    time: str  # e.g., "09:00 AM"
    attraction: Attraction
    duration_hours: float
    notes: Optional[str] = None

class DayItinerary(BaseModel):
    """Represents a single day's plan"""
    day_number: int
    date: Optional[str] = None
    activities: List[Activity] = []
    meals: Optional[List[str]] = None  # e.g., ["Lunch at 12:00 PM", "Dinner at 7:00 PM"]
    accommodation: Optional[str] = None

class Budget(BaseModel):
    accommodation: float
    food: float
    activities: float
    local_transport: float
    flights: Optional[float] = None
    train: Optional[float] = None
    transport: Optional[float] = None
    total: float
    currency: str = "INR"

class TravelPlanResponse(BaseModel):
    destination: DestinationDetails
    attractions: List[Attraction] = []
    # Simplified flight info or airports
    nearby_airports: List[Dict[str, Any]] = []
    flights: List[FlightOffer] = [] 
    recommendations: List[str] = []
    # New fields for automatic planning
    itinerary: Optional[List[DayItinerary]] = None
    travel_mode: Optional[str] = None
    total_days: Optional[int] = None
    estimated_budget: Optional[Budget] = None

