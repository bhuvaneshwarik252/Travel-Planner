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
    Validates connectivity to:
    - Geoapify (Primary Planner)
    - Amadeus (Flights)
    - Unsplash (Images)
    - GeoDB (Standalone)
    - OpenTripMap (Standalone)
    """
    from src.services.geoapify_service import geoapify_service
    
    status = {
        "geoapify": "DOWN",
        "amadeus": "DOWN",
        "unsplash": "DOWN",
        "opentripmap": "DOWN",
        "geodb": "DOWN"
    }

    # 1. Geoapify Check (Geocoding)
    try:
        # Simple geocode check for "London"
        result = await geoapify_service.forward_geocoding("London")
        if result and "lat" in result:
            status["geoapify"] = "UP"
        else:
            logger.warning("Geoapify health check failed: Invalid response")
    except Exception as e:
        logger.error(f"Geoapify Health Check Failed: {e}")

    # 2. Amadeus Check (Flight Search)
    try:
        if travel_service.client:
            result = travel_service.search_locations("LON")
            if isinstance(result, list):
                status["amadeus"] = "UP"
            elif isinstance(result, dict) and "error" in result:
                logger.warning(f"Amadeus API returned error: {result['error']}")
        else:
            logger.warning("Amadeus client not initialized")
    except Exception as e:
        logger.error(f"Amadeus Health Check Failed: {e}")

    # 3. Unsplash Check
    try:
        if settings.UNSPLASH_ACCESS_KEY:
            async with httpx.AsyncClient(timeout=5.0) as client:
                url = "https://api.unsplash.com/search/photos"
                params = {"query": "nature", "per_page": 1, "client_id": settings.UNSPLASH_ACCESS_KEY}
                response = await client.get(url, params=params)
                if response.status_code == 200:
                    status["unsplash"] = "UP"
                else:
                    logger.warning(f"Unsplash API check failed: {response.status_code}")
        else:
            status["unsplash"] = "SKIPPED (No Key)"
    except Exception as e:
        logger.error(f"Unsplash Health Check Failed: {e}")

    # 4. OpenTripMap Check
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            url = "https://api.opentripmap.com/0.1/en/places/radius"
            params = {"radius": 1000, "lon": 0, "lat": 0, "apikey": settings.OPENTRIPMAP_API_KEY}
            response = await client.get(url, params=params)
            if response.status_code == 200:
                status["opentripmap"] = "UP"
            else:
                logger.warning(f"OpenTripMap check failed: {response.status_code}")
    except Exception as e:
        logger.error(f"OpenTripMap Health Check Failed: {e}")

    # 5. GeoDB Cities Check
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            url = f"https://{settings.GEODB_API_HOST}/v1/geo/cities"
            headers = {"X-RapidAPI-Key": settings.GEODB_API_KEY, "X-RapidAPI-Host": settings.GEODB_API_HOST}
            params = {"limit": 1}
            response = await client.get(url, headers=headers, params=params)
            if response.status_code == 200:
                status["geodb"] = "UP"
            else:
                logger.warning(f"GeoDB check failed: {response.status_code}")
    except Exception as e:
        logger.error(f"GeoDB Health Check Failed: {e}")

    return status
