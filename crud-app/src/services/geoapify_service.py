import httpx
import logging
import asyncio
from typing import List, Dict, Optional, Any
from config.settings import settings

logger = logging.getLogger(__name__)

class GeoapifyService:
    """
    Service for interacting with Geoapify API.
    Handles Geocoding (City Search) and Places (Tourist Attractions).
    """
    def __init__(self):
        self.base_url = "https://api.geoapify.com/v2"
        self.api_key = settings.GEOAPIFY_API_KEY
        self.timeout = httpx.Timeout(30.0, connect=10.0)

        if not self.api_key:
            logger.warning("Geoapify API Key is missing. Geoapify features will not work.")

    async def get_places(
        self, 
        lat: float, 
        lon: float, 
        categories: str = "tourism.sights,entertainment", 
        radius: int = 5000, 
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Fetch places (attractions) near a coordinate.
        """
        if not self.api_key:
            return []

        url = f"{self.base_url}/places"
        params = {
            "categories": categories,
            "filter": f"circle:{lon},{lat},{radius}",
            "limit": limit,
            "apiKey": self.api_key
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                logger.info(f"Calling Geoapify Places: {url} params={params}")
                response = await client.get(url, params=params)
                if response.status_code != 200:
                    logger.error(f"Geoapify Error: {response.text}")
                
                response.raise_for_status()
                data = response.json()
                
                features = data.get("features", [])
                if not features:
                    logger.warning(f"Geoapify returned NO features. Raw response: {data}")
                
                # Normalize first
                places = [self._normalize_place(f) for f in features]

                # Enrich with Wikipedia Images Concurrently
                enrich_tasks = []
                for place in places:
                    if place.get("wikipedia_url"):
                         enrich_tasks.append(self._enrich_image(client, place))
                         enrich_tasks.append(self._fetch_wikipedia_summary(client, place))
                
                if enrich_tasks:
                     await asyncio.gather(*enrich_tasks)

                return places

            except httpx.HTTPError as e:
                logger.error(f"Geoapify Places API Error: {e}", exc_info=True)
                if hasattr(e, 'response') and e.response:
                    logger.error(f"Response status: {e.response.status_code}, body: {e.response.text[:500]}")
                return []
            except Exception as e:
                logger.error(f"Unexpected error in GeoapifyService: {e}", exc_info=True)
                return []

    async def _enrich_image(self, client: httpx.AsyncClient, place: Dict[str, Any]):
        """Fetch image from Wikipedia (primary) or Unsplash (fallback)."""
        # 1. Try Wikipedia first if available
        if place.get("wikipedia_url"):
            try:
                # URL is like https://en.wikipedia.org/wiki/Title_With_Spaces
                wiki_url = place.get("wikipedia_url")
                parts = wiki_url.split("//")[1].split("/")
                domain = parts[0] # en.wikipedia.org
                title = parts[-1] 
                
                api_url = f"https://{domain}/w/api.php"
                params = {
                    "action": "query",
                    "prop": "pageimages",
                    "format": "json",
                    "piprop": "original",
                    "titles": title
                }
                headers = {
                    "User-Agent": "TravelPlanner/1.0 (contact@example.com)"
                }

                resp = await client.get(api_url, params=params, headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    pages = data.get("query", {}).get("pages", {})
                    for _, page in pages.items():
                        if "original" in page:
                            place["image"] = page["original"]["source"]
                            return # Found valid image, exit
            except Exception as e:
                logger.warning(f"Failed to fetch wiki image for {place.get('name')}: {e}")

        # 2. Fallback to Unsplash if no image yet
        if not place.get("image") and settings.UNSPLASH_ACCESS_KEY:
            await self._fetch_unsplash_image(client, place)

    async def _fetch_unsplash_image(self, client: httpx.AsyncClient, place: Dict[str, Any]):
        """Search Unsplash for an image using the place name."""
        try:
            url = "https://api.unsplash.com/search/photos"
            params = {
                "query": place.get("name"),
                "per_page": 1,
                "client_id": settings.UNSPLASH_ACCESS_KEY
            }
            resp = await client.get(url, params=params)
            if resp.status_code == 200:
                data = resp.json()
                results = data.get("results", [])
                if results:
                    # Use the 'regular' size URL
                    place["image"] = results[0]["urls"]["regular"]
                    place["image_source"] = "unsplash" # Optional: track source
        except Exception as e:
            logger.warning(f"Unsplash error for {place.get('name')}: {e}")

    async def _fetch_wikipedia_summary(self, client: httpx.AsyncClient, place: Dict[str, Any]):
        """Fetch Wikipedia summary/extract for a place."""
        try:
            wiki_url = place.get("wikipedia_url")
            if not wiki_url:
                return
            
            # Extract title from URL: https://en.wikipedia.org/wiki/Title_Name
            parts = wiki_url.split("/wiki/")
            if len(parts) != 2:
                return
            
            title = parts[1].replace("_", " ")
            domain = wiki_url.split("/")[2]  # e.g., "en.wikipedia.org"
            lang = domain.split(".")[0]  # e.g., "en"
            
            # Use Wikipedia API to get extract (summary)
            api_url = f"https://{lang}.wikipedia.org/w/api.php"
            params = {
                "action": "query",
                "format": "json",
                "prop": "extracts",
                "exintro": True,  # Only intro section
                "explaintext": True,  # Plain text, no HTML
                "titles": title
            }
            
            headers = {
                "User-Agent": "TravelPlanner/1.0 (Educational Project; contact@example.com)"
            }
            
            resp = await client.get(api_url, params=params, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                pages = data.get("query", {}).get("pages", {})
                for page_id, page_data in pages.items():
                    extract = page_data.get("extract")
                    if extract:
                        # Limit to first 2-3 sentences for brevity
                        sentences = extract.split(". ")
                        summary = ". ".join(sentences[:2]) + "." if len(sentences) > 1 else extract
                        place["description"] = summary
                        return
        except Exception as e:
            logger.warning(f"Wikipedia summary error for {place.get('name')}: {e}")

    async def forward_geocoding(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Get coordinates for a city or location name.
        """
        if not self.api_key:
            return None

        url = "https://api.geoapify.com/v1/geocode/search"
        params = {
            "text": text,
            "apiKey": self.api_key,
            "limit": 1
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                features = data.get("features", [])
                if features:
                    return self._normalize_location(features[0])
                return None
            except Exception as e:
                logger.error(f"Geoapify Geocoding Error: {e}")
                return None

    def _normalize_place(self, feature: Dict) -> Dict[str, Any]:
        """Normalize Geoapify place response to application schema."""
        props = feature.get("properties", {})
        geometry = feature.get("geometry", {})
        coordinates = geometry.get("coordinates", [None, None])

        # Extract Wikipedia
        wiki_url = None
        wiki_data = props.get("wiki_and_media", {})
        if "wikipedia" in wiki_data:
            # Format: "en:Bangalore Palace" -> "https://en.wikipedia.org/wiki/Bangalore_Palace"
            parts = wiki_data["wikipedia"].split(":")
            if len(parts) == 2:
                wiki_url = f"https://{parts[0]}.wikipedia.org/wiki/{parts[1].replace(' ', '_')}"
        
        # Extract Image (if available in direct fields, though rare in basic)
        image = props.get("image") # Try direct property

        return {
            "name": props.get("name", props.get("formatted", "Unknown")),
            "kind": props.get("categories", [])[0] if props.get("categories") else "attraction",
            "description": props.get("formatted") or f"A notable place in {props.get('city', 'the area')}", 
            "latitude": coordinates[1],
            "longitude": coordinates[0],
            "address": props.get("formatted"),
            "image": image,
            "wikipedia_url": wiki_url,
            "rating": None # Geoapify places usually don't have ratings in this endpoint
        }

    def _normalize_location(self, feature: Dict) -> Dict[str, Any]:
        """Normalize Geoapify geocoding response."""
        props = feature.get("properties", {})
        return {
            "name": props.get("city", props.get("name", props.get("formatted"))),
            "country": props.get("country"),
            "lat": props.get("lat"),
            "lon": props.get("lon"),
            "formatted": props.get("formatted")
        }
    
    async def get_route(
        self,
        start_lat: float,
        start_lon: float,
        end_lat: float,
        end_lon: float,
        mode: str = "walk"  # walk, drive, transit, bicycle
    ) -> Optional[Dict[str, Any]]:
        """Get route between two points with distance and duration."""
        if not self.api_key:
            return None
        
        url = "https://api.geoapify.com/v1/routing"
        params = {
            "waypoints": f"{start_lat},{start_lon}|{end_lat},{end_lon}",
            "mode": mode,
            "apiKey": self.api_key
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                features = data.get("features", [])
                if features:
                    props = features[0].get("properties", {})
                    return {
                        "distance_meters": props.get("distance"),
                        "duration_seconds": props.get("time"),
                        "mode": mode
                    }
                return None
            except Exception as e:
                logger.error(f"Geoapify Routing Error: {e}")
                return None

geoapify_service = GeoapifyService()
