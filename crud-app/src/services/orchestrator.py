import asyncio
import logging
from typing import Optional, List, Dict, Any

from src.services.geodb_service import geodb_service
from src.services.places_service import places_service
from src.services.travel_service import travel_service
from src import schemas

logger = logging.getLogger(__name__)

class OrchestratorService:
    async def generate_travel_plan(
        self, 
        destination_name: str, 
        origin_code: Optional[str] = None, 
        travel_date: Optional[str] = None
    ) -> schemas.TravelPlanResponse:
        
        logger.info(f"Orchestrating travel plan for: {destination_name}")

        # Step 1: GeoDB - Get Destination Details
        city_info = await geodb_service.get_city_details(destination_name)
        
        if "error" in city_info:
            raise ValueError(f"Destination '{destination_name}' not found.")

        destination_details = schemas.DestinationDetails(
            name=city_info.get("name"),
            country=city_info.get("country"),
            region=city_info.get("region"),
            population=city_info.get("population"),
            coordinates=schemas.Coordinates(
                latitude=city_info.get("lat"), 
                longitude=city_info.get("lon")
            )
        )

        # Step 2: Places Service - Get Attractions
        attractions_list = []
        try:
            places_data = await places_service.get_tourist_places(destination_name, limit=5)
            if "attractions" in places_data:
                for attr in places_data["attractions"]:
                    attractions_list.append(schemas.Attraction(
                        name=attr.get("name"),
                        kind=attr.get("kind"),
                        description=attr.get("description"),
                        image=attr.get("image"),
                        coordinates=schemas.Coordinates(
                            latitude=attr.get("latitude"),
                            longitude=attr.get("longitude")
                        )
                    ))
        except Exception as e:
            logger.error(f"Error fetching attractions in orchestrator: {e}")

        # Step 3: Travel Service - Flights and Nearby Airports
        nearby_airports = []
        flight_offers = []
        
        try:
            # 3a. Flights (if params provided)
            if origin_code and travel_date:
                # Travel service now handles city name resolution and INR internally
                flight_result = travel_service.search_flights(
                    origin=origin_code, 
                    destination=destination_name, 
                    departure_date=travel_date
                )
                
                if "flights" in flight_result and isinstance(flight_result["flights"], list):
                    # Process top 3 flights
                    for offer in flight_result["flights"][:3]:
                        price = offer.get("price", {})
                        itineraries = offer.get("itineraries", [])
                        
                        if itineraries:
                            segments = itineraries[0].get("segments", [])
                            if segments:
                                first_seg = segments[0]
                                last_seg = segments[-1]
                                
                                # Use enriched airline name if available, else code
                                airline = first_seg.get("airlineName", first_seg.get("carrierCode"))
                                dep_at = first_seg.get("departure", {}).get("at")
                                arr_at = last_seg.get("arrival", {}).get("at")
                                duration = itineraries[0].get("duration")

                                flight_offers.append(schemas.FlightOffer(
                                    price=str(price.get("total")),
                                    currency=price.get("currency", "INR"),
                                    airline=airline,
                                    departure=dep_at,
                                    arrival=arr_at,
                                    duration=duration
                                ))

            # 3b. Nearby Airports/Locations (Optional enrichment)
            loc_results = travel_service.search_locations(destination_name)
            if isinstance(loc_results, list):
                for loc in loc_results:
                    if loc.get("subType") in ["AIRPORT", "CITY"]:
                         nearby_airports.append({
                             "name": loc.get("name"),
                             "iataCode": loc.get("iataCode"),
                             "subType": loc.get("subType")
                         })

        except Exception as e:
             logger.error(f"Error fetching travel info in orchestrator: {e}")

        # Step 4: Final Recommendations
        recommendations = []
        if attractions_list:
            recommendations.append(f"Must visit: {attractions_list[0].name}")
        if flight_offers:
             recommendations.append(f"Best flight price: {flight_offers[0].price} {flight_offers[0].currency}")
        
        return schemas.TravelPlanResponse(
            destination=destination_details,
            attractions=attractions_list,
            nearby_airports=nearby_airports,
            flights=flight_offers,
            recommendations=recommendations
        )

# Global Instance
orchestrator_service = OrchestratorService()
