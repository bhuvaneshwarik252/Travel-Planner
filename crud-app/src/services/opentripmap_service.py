import httpx
import asyncio
import logging
from typing import List, Dict, Optional, Any
from config.settings import settings

logger = logging.getLogger(__name__)

class OpenTripMapService:
    """
    Dedicated OpenTripMap service module for retrieving normalized 
    tourist attractions and cultural data.
    """
    def __init__(self):
        self.base_url = "https://api.opentripmap.com/0.1/en"
        self.api_key = settings.OPENTRIPMAP_API_KEY
        self.timeout = httpx.Timeout(10.0, connect=5.0)

    async def get_attractions(
        self, 
        lat: float, 
        lon: float, 
        radius: int = 15000, 
        limit: int = 10,
        kinds: str = "amusements,interesting_places,tourist_facilities"
    ) -> List[Dict[str, Any]]:
        """
        Main function to retrieve normalized points of interest.
        Performs a radius search and enriches results with details.
        """
        if not self.api_key:
            logger.error("OpenTripMap API Key is missing in environment variables")
            return []

        search_url = f"{self.base_url}/places/radius"
        # Ensure lat/lon are floats and radius is integer
        params = {
            "apikey": self.api_key,
            "radius": int(radius),
            "lon": float(lon),
            "lat": float(lat),
            "kinds": kinds,
            "limit": limit,
            "format": "json"
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                # 1. Radius Search
                response = await client.get(search_url, params=params)
                if response.status_code != 200:
                    logger.error(f"OpenTripMap Search Error: {response.status_code} - {response.text}")
                    return []
                
                raw_places = response.json()
                logger.info(f"OpenTripMap: Found {len(raw_places)} raw results for lat={lat}, lon={lon}")

                if not raw_places or not isinstance(raw_places, list):
                    # Try a larger radius as fallback if 0 results
                    if radius < 50000:
                        logger.info(f"No results found within {radius}m, trying 30km radius...")
                        return await self.get_attractions(lat, lon, radius=30000, limit=limit, kinds=kinds)
                    return []

                # 2. Concurrent Enrichment (XID Lookups)
                # This is crucial because radius search often lacks descriptions/images
                tasks = [self._fetch_details(client, place.get("xid")) for place in raw_places if "xid" in place]
                details_results = await asyncio.gather(*tasks, return_exceptions=True)

                # 3. Normalization
                normalized_list = []
                for i, raw_place in enumerate(raw_places):
                    detail = details_results[i] if not isinstance(details_results[i], Exception) else None
                    normalized = self._normalize_attraction(raw_place, detail)
                    
                    # We only filter if there's absolutely NO name found anywhere
                    if normalized.get("name") and normalized.get("name") != "Unknown":
                        normalized_list.append(normalized)

                return normalized_list

            except httpx.HTTPError as e:
                logger.error(f"OpenTripMap API Failure: {e}")
                return []
            except Exception as e:
                logger.error(f"Unexpected error in OpenTripMapService: {e}")
                return []

    async def _fetch_details(self, client: httpx.AsyncClient, xid: str) -> Optional[Dict]:
        """Fetch full details for an attraction by its unique ID."""
        if not xid:
            return None
        url = f"{self.base_url}/places/xid/{xid}"
        try:
            response = await client.get(url, params={"apikey": self.api_key})
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.debug(f"Failed to fetch XID {xid}: {e}")
            return None

    def _normalize_attraction(self, raw_place: Dict, details: Optional[Dict]) -> Dict[str, Any]:
        """
        Normalize raw API responses into a clean application schema.
        Maps fields to align with both User Request and existing Schemas.
        """
        point = raw_place.get("point", {})
        kinds = raw_place.get("kinds", "").split(",")
        category = kinds[0] if kinds else "attraction"

        # Initialize with base data from radius search
        normalized = {
            "name": raw_place.get("name", "Unknown"),
            "kind": category,
            "description": None,
            "latitude": point.get("lat"),
            "longitude": point.get("lon"),
            "image": None,
            "wikipedia_url": None,
            "rating": raw_place.get("rate", 0)
        }

        # Enrich with details if fetch was successful
        if details:
            # Overwrite name if detail has a more specific one
            if details.get("name"):
                normalized["name"] = details.get("name")
            
            # Category can be more descriptive in details
            if "kinds" in details:
                normalized["kind"] = details["kinds"].split(",")[0]

            # Extract description
            wiki = details.get("wikipedia_extracts", {})
            normalized["description"] = wiki.get("text")
            
            # Extract Image 
            normalized["image"] = details.get("preview", {}).get("source") or details.get("image")
            
            # Wiki URL
            normalized["wikipedia_url"] = details.get("wikipedia")
            
            # Coordinates (often more precise in details)
            if "point" in details:
                 normalized["latitude"] = details["point"].get("lat")
                 normalized["longitude"] = details["point"].get("lon")

        return normalized

# Global instance for easy import
opentripmap_service = OpenTripMapService()
