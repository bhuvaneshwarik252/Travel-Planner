from amadeus import Client, ResponseError, Location
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

class TravelService:
    def __init__(self):
        self.client = None
        if settings.AMADEUS_CLIENT_ID and settings.AMADEUS_CLIENT_SECRET:
            try:
                self.client = Client(
                    client_id=settings.AMADEUS_CLIENT_ID,
                    client_secret=settings.AMADEUS_CLIENT_SECRET
                )
                logger.info("Amadeus Client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Amadeus client: {e}")
        else:
            logger.warning("Amadeus credentials not found in settings")

    def search_locations(self, keyword: str):
        """
        Search for cities or airports by keyword.
        """
        if not self.client:
            return {"error": "Amadeus client not initialized"}
        
        try:
            response = self.client.reference_data.locations.get(
                keyword=keyword,
                subType=Location.ANY
            )
            return response.data
        except ResponseError as error:
            logger.error(f"Amadeus API Error: {error}")
            return {"error": str(error)}

    def search_flights(self, origin: str, destination: str, departure_date: str, adults: int = 1):
        """
        Search for flight offers.
        """
        if not self.client:
            return {"error": "Amadeus client not initialized"}

        try:
            response = self.client.shopping.flight_offers_search.get(
                originLocationCode=origin,
                destinationLocationCode=destination,
                departureDate=departure_date,
                adults=adults
            )
            return response.data
        except ResponseError as error:
            logger.error(f"Amadeus API Error: {error}")
            return {"error": str(error)}

# Global instance
travel_service = TravelService()
