from amadeus import Client, ResponseError, Location
from typing import Optional, Dict, List, Any
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

class TravelService:
    def __init__(self):
        self.client = None
        self._location_cache = {} # Simple in-memory cache
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

    def _resolve_location(self, keyword: str) -> Optional[Dict[str, str]]:
        """
        Helper to resolve a city/airport name to an IATA code and Name.
        Use local cache to avoid redundant API calls.
        """
        if keyword in self._location_cache:
            return self._location_cache[keyword]

        # If it looks like an IATA code, try to find its name
        if len(keyword) == 3 and keyword.isalpha() and keyword.isupper():
            try:
                response = self.client.reference_data.locations.get(
                    keyword=keyword,
                    subType=Location.ANY
                )
                if response.data:
                    for loc in response.data:
                        if loc.get('iataCode') == keyword:
                            info = {'iataCode': loc.get('iataCode'), 'name': loc.get('name')}
                            self._location_cache[keyword] = info
                            return info
                return {'iataCode': keyword, 'name': keyword} 
            except:
                return {'iataCode': keyword, 'name': keyword}

        try:
            # Search for the location using ANY (City or Airport)
            # This is broader and more likely to find matches for "bengalore" etc.
            response = self.client.reference_data.locations.get(
                keyword=keyword,
                subType=Location.ANY
            )
            
            if response.data:
                # Prefer AIRPORT or CITY with high relevance
                # But simply taking the first one is often good enough for Amadeus
                best_match = response.data[0]
                info = {'iataCode': best_match.get('iataCode'), 'name': best_match.get('name')}
                self._location_cache[keyword] = info
                return info
            
        except ResponseError as error:
            logger.error(f"Error resolving location for '{keyword}': {error}")
            return None
        
        return None

    def _enrich_flight_data(self, flights: List[Dict], dictionaries: Dict):
        """
        Post-processes flights to replace codes with names for cities and carriers.
        """
        carriers = dictionaries.get('carriers', {})
        
        for flight in flights:
            # Add full airline names based on dictionary
            v_airline_codes = flight.get('validatingAirlineCodes', [])
            flight['airlines'] = [carriers.get(code, code) for code in v_airline_codes]
            
            for itinerary in flight.get('itineraries', []):
                for segment in itinerary.get('segments', []):
                    # Enrich Departure
                    dep = segment.get('departure', {})
                    dep_code = dep.get('iataCode')
                    if dep_code:
                        loc_info = self._resolve_location(dep_code)
                        dep['cityName'] = loc_info['name'] if loc_info else dep_code
                    
                    # Enrich Arrival
                    arr = segment.get('arrival', {})
                    arr_code = arr.get('iataCode')
                    if arr_code:
                        loc_info = self._resolve_location(arr_code)
                        arr['cityName'] = loc_info['name'] if loc_info else arr_code
                    
                    # Enrich Carrier
                    c_code = segment.get('carrierCode')
                    if c_code:
                        segment['airlineName'] = carriers.get(c_code, c_code)

    def search_flights(self, origin: str, destination: str, departure_date: str, adults: int = 1):
        """
        Search for flight offers.
        Automatically resolves city names to IATA codes and sets currency to INR.
        """
        if not self.client:
            return {"error": "Amadeus client not initialized"}

        # Resolve Origin
        origin_info = self._resolve_location(origin)
        if not origin_info:
            return {"error": f"Could not find location for origin: '{origin}'"}

        # Resolve Destination
        dest_info = self._resolve_location(destination)
        if not dest_info:
            return {"error": f"Could not find location for destination: '{destination}'"}

        logger.info(f"Searching flights: {origin_info['name']} ({origin_info['iataCode']}) -> {dest_info['name']} ({dest_info['iataCode']}) in INR")

        try:
            response = self.client.shopping.flight_offers_search.get(
                originLocationCode=origin_info['iataCode'],
                destinationLocationCode=dest_info['iataCode'],
                departureDate=departure_date,
                adults=adults,
                currencyCode='INR'
            )
            
            flights = response.data
            dictionaries = response.result.get('dictionaries', {})
            
            # Enrich all flight data with names
            self._enrich_flight_data(flights, dictionaries)

            return {
                "origin": origin_info,
                "destination": dest_info,
                "flights": flights
            }
        except ResponseError as error:
            logger.error(f"Amadeus API Error: {error}")
            return {"error": str(error)}

# Global instance
travel_service = TravelService()
