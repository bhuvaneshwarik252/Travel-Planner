import httpx
import logging
import asyncio
from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta
from config.settings import settings

logger = logging.getLogger(__name__)

class GeoDBService:
    def __init__(self):
        self.base_url = "https://wft-geo-db.p.rapidapi.com/v1/geo"
        self.headers = {
            "X-RapidAPI-Key": settings.GEODB_API_KEY,
            "X-RapidAPI-Host": settings.GEODB_API_HOST
        }
        # Simple in-memory cache: {key: (data, expiry_timestamp)}
        self._cache: Dict[str, tuple[Any, datetime]] = {}
        self._cache_ttl_minutes = 60

    def _get_from_cache(self, key: str) -> Optional[Any]:
        if key in self._cache:
            data, expiry = self._cache[key]
            if datetime.now() < expiry:
                return data
            else:
                del self._cache[key]
        return None

    def _set_cache(self, key: str, value: Any):
        expiry = datetime.now() + timedelta(minutes=self._cache_ttl_minutes)
        self._cache[key] = (value, expiry)

    async def _request(self, method: str, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """Internal helper to handle requests with error handling and logging."""
        url = f"{self.base_url}{endpoint}"
        cache_key = f"{method}:{url}:{str(params)}"
        
        cached = self._get_from_cache(cache_key)
        if cached:
            return cached

        if not settings.GEODB_API_KEY:
            logger.error("GeoDB API Key not configured")
            return None

        async with httpx.AsyncClient() as client:
            try:
                response = await client.request(method, url, headers=self.headers, params=params)
                response.raise_for_status()
                data = response.json()
                self._set_cache(cache_key, data)
                return data
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    return None
                logger.error(f"GeoDB API Error: {e.response.text}")
                return None
            except Exception as e:
                logger.error(f"GeoDB Connection Error: {e}")
                return None

    def _normalize_city(self, data: Dict) -> Dict:
        """
        Normalize GeoDB city response to app schema.
        Removes internal IDs and flattens coordinates.
        """
        return {
            "name": data.get("name"),
            "country": data.get("country"),
            "region": data.get("region"),
            "population": data.get("population"),
            "lat": data.get("latitude"),
            "lon": data.get("longitude")
        }

    async def _find_cities_raw(self, name_prefix: str, limit: int = 5) -> List[Dict]:
        """Internal helper to get raw city data (preserving IDs)."""
        params = {
            "namePrefix": name_prefix,
            "limit": limit,
            "sort": "-population",
            "types": "CITY"
        }
        result = await self._request("GET", "/cities", params=params)
        if not result or "data" not in result:
            return []
        return result["data"]

    async def find_cities(self, name_prefix: str, limit: int = 5) -> List[Dict]:
        """Find cities by name prefix and return normalized data."""
        raw_cities = await self._find_cities_raw(name_prefix, limit)
        return [self._normalize_city(city) for city in raw_cities]

    async def get_city_details(self, city_name_or_id: str) -> Dict:
        """
        Get details for a city by name or ID.
        Response is fully normalized and includes nearby cities.
        """
        raw_city = None
        
        # 1. Search by name if it looks like a name
        if city_name_or_id.replace(" ", "").isalpha() and len(city_name_or_id) > 1:
             search_results = await self._find_cities_raw(city_name_or_id, limit=1)
             if search_results:
                 raw_city = search_results[0]
        
        # 2. If not found or looks like ID, try fetching as ID directly
        if not raw_city:
             direct_result = await self._request("GET", f"/cities/{city_name_or_id}")
             if direct_result and "data" in direct_result:
                 raw_city = direct_result["data"]

        # 3. Last resort fallback search
        if not raw_city and not (city_name_or_id.replace(" ", "").isalpha()):
             search_results = await self._find_cities_raw(city_name_or_id, limit=1)
             if search_results:
                 raw_city = search_results[0]

        if not raw_city:
            return {"error": f"City '{city_name_or_id}' not found"}

        # ID needed only internally for nearby search
        city_id = raw_city.get("id")
        
        normalized_city = self._normalize_city(raw_city)
        
        if city_id:
            nearby = await self.get_nearby_cities(city_id)
            normalized_city["nearby_cities"] = nearby
        else:
            normalized_city["nearby_cities"] = []
            
        return normalized_city

    async def get_nearby_cities(self, city_id: Any, radius: int = 100) -> List[Dict]:
        """Fetch nearby cities using cityId and return normalized list."""
        if not city_id:
            return []
            
        params = {
            "radius": radius,
            "limit": 5,
            "sort": "-population",
            "types": "CITY"
        }
        
        result = await self._request("GET", f"/cities/{city_id}/nearbyCities", params=params)
        if not result or "data" not in result:
            return []
            
        return [self._normalize_city(city) for city in result["data"]]

geodb_service = GeoDBService()
