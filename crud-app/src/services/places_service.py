import logging
from typing import Dict, Any
from src.services.geodb_service import geodb_service
from src.services.opentripmap_service import opentripmap_service

logger = logging.getLogger(__name__)

class PlacesService:
    """
    Orchestration service that combines GeoDB location resolution 
    with OpenTripMap attraction retrieval.
    """
    async def get_tourist_places(self, location_name: str, limit: int = 10) -> Dict[str, Any]:
        """
        Main entry point for retrieving attractions for a specific city/region.
        Delegates coordination to geodb_service and lookup to opentripmap_service.
        """
        # 1. Resolve Location (Name -> Coordinates)
        city_info = await geodb_service.get_city_details(location_name)
        if "error" in city_info:
            return {"error": city_info["error"]}
        
        lat = city_info.get("lat")
        lon = city_info.get("lon")
        
        if lat is None or lon is None:
             return {"error": "Could not resolve location coordinates"}

        # 2. Fetch Normalized Attractions via OpenTripMap module
        # This keeps API-specific logic (XID lookups, kinds, etc.) in one place.
        attractions = await opentripmap_service.get_attractions(
            lat=lat, 
            lon=lon, 
            limit=limit
        )

        # Cleanup city_info metadata
        city_info.pop("nearby_cities", None)

        return {
            "location": city_info,
            "attractions": attractions
        }

# Global instance
places_service = PlacesService()
