from fastapi import APIRouter
import httpx
import logging
from src.services.travel_service import travel_service
from config.settings import settings

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/health/apis", tags=["health"])
async def check_apis():
    """
    Health check for external APIs.
    Validates connectivity to Amadeus, OpenTripMap, and GeoDB Cities.
    """
    status = {
        "amadeus": "DOWN",
        "opentripmap": "DOWN",
        "geodb": "DOWN"
    }

    # 1. Amadeus Check (Validate API call)
    try:
        if travel_service.client:
            # Perform a lightweight search to validate connectivity
            # We use a broad search for "LON" (London) which should always return results
            result = travel_service.search_locations("LON")
            
            # Check if result is a list (success) or dict with error
            if isinstance(result, list):
                status["amadeus"] = "UP"
            elif isinstance(result, dict) and "error" in result:
                logger.warning(f"Amadeus API returned error: {result['error']}")
            else:
                 # If we get here, it might be a successful dict response (unlikely for this endpoint but check)
                 status["amadeus"] = "UP"
        else:
            logger.warning("Amadeus client not initialized in TravelService")
    except Exception as e:
        logger.error(f"Amadeus Health Check Failed: {e}")
        status["amadeus"] = "DOWN"

    # 2. OpenTripMap Check (Simple places/radius)
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            url = "https://api.opentripmap.com/0.1/en/places/radius"
            params = {
                "radius": 1000,
                "lon": 0,
                "lat": 0,
                "apikey": settings.OPENTRIPMAP_API_KEY
            }
            response = await client.get(url, params=params)
            
            if response.status_code == 200:
                status["opentripmap"] = "UP"
            else:
                logger.warning(f"OpenTripMap API check failed with status: {response.status_code}")
    except Exception as e:
        logger.error(f"OpenTripMap Health Check Failed: {e}")
        status["opentripmap"] = "DOWN"

    # 3. GeoDB Cities Check (List cities limit=1)
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            url = f"https://{settings.GEODB_API_HOST}/v1/geo/cities"
            headers = {
                "X-RapidAPI-Key": settings.GEODB_API_KEY,
                "X-RapidAPI-Host": settings.GEODB_API_HOST
            }
            params = {"limit": 1}
            
            response = await client.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                status["geodb"] = "UP"
            else:
                logger.warning(f"GeoDB Cities API check failed with status: {response.status_code}")
    except Exception as e:
        logger.error(f"GeoDB Cities Health Check Failed: {e}")
        status["geodb"] = "DOWN"

    return status
