from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List, Any, Dict

# Shared properties
class UserBase(BaseModel):
    name: str
    email: EmailStr

# Properties to receive via API on creation
class UserCreate(UserBase):
    pass

# Properties to receive via API on update (all optional)
class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None

# Properties to return to client
class UserResponse(UserBase):
    id: int
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

class TravelPlanResponse(BaseModel):
    destination: DestinationDetails
    attractions: List[Attraction] = []
    # Simplified flight info or airports
    nearby_airports: List[Dict[str, Any]] = []
    flights: List[FlightOffer] = [] 
    recommendations: List[str] = []
