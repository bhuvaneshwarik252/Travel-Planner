from fastapi import APIRouter, HTTPException, Query
from src.services.travel_service import travel_service
from src.services.geodb_service import geodb_service
from typing import Optional

router = APIRouter()

# ... (existing endpoints) ...

@router.get("/cities/search")
async def find_cities(
    name: str = Query(..., min_length=3, description="City name prefix (e.g., Lon)"),
    limit: int = Query(5, ge=1, le=10)
):
    """
    Find cities using GeoDB API.
    Returns city info including the WikiDataId (used for details).
    """
    return await geodb_service.find_cities(name, limit)

@router.get("/cities/{city_id}")
async def get_city_details(city_id: str):
    """
    Get detailed info about a city using its WikiDataId (e.g., Q60).
    """
    return await geodb_service.get_city_details(city_id)

@router.get("/locations")
def search_locations(keyword: str = Query(..., min_length=3, description="City or airport name")):
    """
    Search for travel locations (cities, airports).
    """
    if not travel_service.client:
        raise HTTPException(status_code=503, detail="Travel service unavailable (Check API Keys)")
    
    result = travel_service.search_locations(keyword)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.get("/flights")
def search_flights(
    origin: str = Query(..., min_length=3, max_length=3, description="IATA code (e.g., LON)"),
    destination: str = Query(..., min_length=3, max_length=3, description="IATA code (e.g., NYC)"),
    departure_date: str = Query(..., description="YYYY-MM-DD"),
    adults: int = Query(1, ge=1, le=9)
):
    """
    Search for flight offers between two destinations.
    """
    if not travel_service.client:
        raise HTTPException(status_code=503, detail="Travel service unavailable (Check API Keys)")

    result = travel_service.search_flights(origin, destination, departure_date, adults)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result
