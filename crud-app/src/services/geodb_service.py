import httpx
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

class GeoDBService:
    def __init__(self):
        self.base_url = "https://wft-geo-db.p.rapidapi.com/v1/geo"
        self.headers = {
            "X-RapidAPI-Key": settings.GEODB_API_KEY,
            "X-RapidAPI-Host": settings.GEODB_API_HOST
        }

    async def get_city_details(self, city_id: str):
        """
        Get details for a specific city by QID (e.g., Q60 for New York).
        """
        if not settings.GEODB_API_KEY:
             return {"error": "GeoDB API Key not configured"}

        url = f"{self.base_url}/cities/{city_id}"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                logger.error(f"GeoDB API Error: {e.response.text}")
                return {"error": f"API Error: {e.response.status_code}"}
            except Exception as e:
                logger.error(f"GeoDB Connection Error: {e}")
                return {"error": str(e)}

    async def find_cities(self, name_prefix: str, limit: int = 5):
        """
        Find cities by name prefix.
        """
        if not settings.GEODB_API_KEY:
             return {"error": "GeoDB API Key not configured"}

        url = f"{self.base_url}/cities"
        params = {
            "namePrefix": name_prefix,
            "limit": limit,
            "sort": "-population"
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logger.error(f"GeoDB Search Error: {e}")
                return {"error": str(e)}

geodb_service = GeoDBService()
