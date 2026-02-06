import asyncio
import logging
from typing import Optional, List, Dict, Any

from src.services.geodb_service import geodb_service
from src.services.places_service import places_service
from src.services.geoapify_service import geoapify_service
from src.services.travel_service import travel_service
from src import schemas

logger = logging.getLogger(__name__)

class OrchestratorService:
    async def generate_travel_plan(
        self, 
        destination_name: str, 
        origin_code: Optional[str] = None, 
        travel_date: Optional[str] = None,
        days: int = 1,
        travel_mode: str = "flight"
    ) -> schemas.TravelPlanResponse:
        
        logger.info(f"Orchestrating travel plan for: {destination_name}")

        # Step 0: Parse Destinations
        destinations = [d.strip() for d in destination_name.split(",") if d.strip()]
        if len(destinations) > 1:
            return await self._generate_multi_city_plan(
                destinations, origin_code, travel_date, days, travel_mode
            )

        # Single Destination Logic
        # Step 1: Geoapify - Get Destination Details via Geocoding
        location_data = await geoapify_service.forward_geocoding(destination_name)
        
        if not location_data:
            raise ValueError(f"Destination '{destination_name}' not found.")

        destination_details = schemas.DestinationDetails(
            name=location_data.get("name"),
            country=location_data.get("country"),
            region=None,
            population=None,
            coordinates=schemas.Coordinates(
                latitude=location_data.get("lat"), 
                longitude=location_data.get("lon")
            )
        )

        # Step 2: Geoapify - Get Attractions with Images
        attractions_list = await self._fetch_attractions(location_data)

        # Step 3: Travel Service - Flights and Nearby Airports
        nearby_airports, flight_offers = self._fetch_travel_info(
            destination_name, origin_code, travel_date
        )

        # Step 4: Generate Day-by-Day Itinerary
        itinerary = []
        if days > 0 and attractions_list:
            itinerary = await self._generate_itinerary(
                attractions=attractions_list, 
                days=days, 
                start_date=travel_date,
                origin=origin_code,
                destination_name=destination_name,
                travel_mode=travel_mode,
                flights=flight_offers
            )
        
        # Step 5: Budget Estimation
        estimated_budget = self._calculate_budget(days, flight_offers, travel_mode)
        
        # Step 6: Final Recommendations
        recommendations = self._generate_recommendations(attractions_list, flight_offers, days)
        
        return schemas.TravelPlanResponse(
            destination=destination_details,
            attractions=attractions_list,
            nearby_airports=nearby_airports,
            flights=flight_offers,
            recommendations=recommendations,
            itinerary=itinerary if itinerary else None,
            travel_mode=travel_mode,
            total_days=days,
            estimated_budget=estimated_budget
        )
    
    async def _generate_itinerary(
        self, 
        attractions: List[schemas.Attraction], 
        days: int,
        start_date: Optional[str] = None,
        origin: Optional[str] = None,
        destination_name: str = "",
        travel_mode: str = "flight",
        flights: List[schemas.FlightOffer] = []
    ) -> List[schemas.DayItinerary]:
        """Generate complete end-to-end itinerary including departure, activities, and return"""
        from datetime import datetime, timedelta
        
        itinerary = []
        attraction_index = 0
        
        for day_num in range(1, days + 1):
            # Calculate date if start_date provided
            day_date = None
            if start_date:
                try:
                    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
                    day_dt = start_dt + timedelta(days=day_num - 1)
                    day_date = day_dt.strftime("%Y-%m-%d")
                except:
                    pass
            
            activities = []
            meals = []
            accommodation = None
            
            # DAY 1: Departure and Arrival
            if day_num == 1:
                # Morning: Departure from origin
                if origin:
                    departure_note = f"Depart from {origin} to {destination_name}"
                    if flights and len(flights) > 0:
                        flight = flights[0]
                        departure_note = f"Flight from {origin}: {flight.airline} - Departs {flight.departure}, Arrives {flight.arrival} ({flight.duration})"
                    elif travel_mode == "train":
                        departure_note = f"Train journey from {origin} to {destination_name}"
                    elif travel_mode in ["car", "bus"]:
                        departure_note = f"{travel_mode.title()} journey from {origin} to {destination_name}"
                    
                    # Create a dummy attraction for travel
                    travel_attraction = schemas.Attraction(
                        name=f"Travel: {origin} → {destination_name}",
                        kind="travel",
                        description=departure_note,
                        image=None,
                        wikipedia_url=None,
                        coordinates=None
                    )
                    activities.append(schemas.Activity(
                        time="06:00",
                        attraction=travel_attraction,
                        duration_hours=3.0,
                        notes=departure_note
                    ))
                
                # Afternoon: Light sightseeing after arrival
                activities_count = min(2, len(attractions) - attraction_index)
                current_time = 14  # 2 PM arrival
                
                for i in range(activities_count):
                    if attraction_index >= len(attractions):
                        break
                    
                    attraction = attractions[attraction_index]
                    time_str = f"{current_time:02d}:00"
                    duration = 1.5
                    
                    # Add transit info from previous attraction
                    notes = f"Explore {attraction.name}"
                    if i > 0 and attraction_index > 0:
                        prev_attraction = attractions[attraction_index - 1]
                        if prev_attraction.coordinates and attraction.coordinates:
                            transit_info = await self._get_transit_suggestion(
                                prev_attraction.coordinates.latitude,
                                prev_attraction.coordinates.longitude,
                                attraction.coordinates.latitude,
                                attraction.coordinates.longitude,
                                destination_name
                            )
                            if transit_info:
                                notes = f"{transit_info} | {notes}"
                    
                    activities.append(schemas.Activity(
                        time=time_str,
                        attraction=attraction,
                        duration_hours=duration,
                        notes=notes
                    ))
                    
                    current_time += int(duration) + 1
                    attraction_index += 1
                
                meals = ["Lunch after arrival", "Dinner at hotel"]
                accommodation = f"Hotel in {destination_name} city center"
            
            # MIDDLE DAYS: Full day activities
            elif day_num < days:
                activities_count = min(4, len(attractions) - attraction_index)
                current_time = 9  # Start at 9 AM
                
                for i in range(activities_count):
                    if attraction_index >= len(attractions):
                        break
                    
                    attraction = attractions[attraction_index]
                    time_str = f"{current_time:02d}:00"
                    duration = 2.0 if i == 0 else 1.5
                    
                    # Add transit info from previous attraction
                    notes = f"Explore {attraction.name}"
                    if i > 0 and attraction_index > 0:
                        prev_attraction = attractions[attraction_index - 1]
                        if prev_attraction.coordinates and attraction.coordinates:
                            transit_info = await self._get_transit_suggestion(
                                prev_attraction.coordinates.latitude,
                                prev_attraction.coordinates.longitude,
                                attraction.coordinates.latitude,
                                attraction.coordinates.longitude,
                                destination_name
                            )
                            if transit_info:
                                notes = f"{transit_info} | {notes}"
                    
                    activities.append(schemas.Activity(
                        time=time_str,
                        attraction=attraction,
                        duration_hours=duration,
                        notes=notes
                    ))
                    
                    current_time += int(duration) + 1
                    attraction_index += 1
                
                meals = ["Breakfast at hotel", "Lunch break at 12:30 PM", "Dinner at 7:00 PM"]
                accommodation = f"Hotel in {destination_name}"
            
            # LAST DAY: Morning activities + Return journey
            else:
                # Morning: Quick sightseeing before departure
                activities_count = min(1, len(attractions) - attraction_index)
                current_time = 9
                
                for i in range(activities_count):
                    if attraction_index >= len(attractions):
                        break
                    
                    attraction = attractions[attraction_index]
                    time_str = f"{current_time:02d}:00"
                    
                    activities.append(schemas.Activity(
                        time=time_str,
                        attraction=attraction,
                        duration_hours=1.5,
                        notes=f"Final visit to {attraction.name}"
                    ))
                    
                    attraction_index += 1
                
                # Afternoon: Return journey
                if origin:
                    return_note = f"Return to {origin} from {destination_name}"
                    if travel_mode == "flight":
                        return_note = f"Flight back to {origin} - Check-out and airport transfer"
                    elif travel_mode == "train":
                        return_note = f"Train journey back to {origin}"
                    elif travel_mode in ["car", "bus"]:
                        return_note = f"{travel_mode.title()} journey back to {origin}"
                    
                    return_attraction = schemas.Attraction(
                        name=f"Return: {destination_name} → {origin}",
                        kind="travel",
                        description=return_note,
                        image=None,
                        wikipedia_url=None,
                        coordinates=None
                    )
                    activities.append(schemas.Activity(
                        time="14:00",
                        attraction=return_attraction,
                        duration_hours=3.0,
                        notes=return_note
                    ))
                
                meals = ["Breakfast at hotel", "Lunch before departure"]
                accommodation = None  # Returning home
            
            itinerary.append(schemas.DayItinerary(
                day_number=day_num,
                date=day_date,
                activities=activities,
                meals=meals,
                accommodation=accommodation
            ))
        
        return itinerary
    
    async def _get_transit_suggestion(
        self,
        start_lat: float,
        start_lon: float,
        end_lat: float,
        end_lon: float,
        city_name: str
    ) -> Optional[str]:
        """Get smart transit suggestion based on distance."""
        import math
        
        # Try walking first (up to ~20 mins / 1.5km)
        route_walk = await geoapify_service.get_route(
            start_lat, start_lon, end_lat, end_lon, mode="walk"
        )
        
        if route_walk:
            dist = int(route_walk.get("distance_meters", 0))
            time_sec = route_walk.get("duration_seconds", 0)
            mins = int(time_sec / 60)
            
            if dist < 1500: # If less than 1.5km, suggest walking
                return f"🚶 Walk {dist}m ({mins} mins)"

        # If too far or walk failed, try transit
        route_transit = await geoapify_service.get_route(
            start_lat, start_lon, end_lat, end_lon, mode="transit"
        )
        
        if route_transit:
            dist = int(route_transit.get("distance_meters", 0))
            time_sec = route_transit.get("duration_seconds", 0)
            mins = int(time_sec / 60)
            return f"🚌 Transit {dist}m ({mins} mins)"
            
        # Fallback if API returns nothing (or generic logic)
        transit_map = {
            "Bangalore": "BMTC", "Bengaluru": "BMTC", "Mumbai": "BEST",
            "Delhi": "DTC", "Kolkata": "WBTC", "Chennai": "MTC", "Hyderabad": "TSRTC"
        }
        transit_name = transit_map.get(city_name, "Local Transport")
        return f"🚕 Take {transit_name} or Taxi (Route not found)"
    
    def _calculate_budget(
        self, 
        days: int, 
        flights: List[schemas.FlightOffer],
        travel_mode: str
    ) -> schemas.Budget:
        """Estimate total trip budget"""
        budget = {
            "accommodation": days * 3000.0,
            "food": days * 1500.0,
            "activities": days * 1000.0,
            "local_transport": days * 500.0,
            "currency": "INR"
        }
        
        # Add flight cost if available
        if flights and travel_mode == "flight":
            try:
                budget["flights"] = float(flights[0].price)
            except:
                budget["flights"] = 10000.0
        elif travel_mode == "train":
            budget["train"] = days * 1000.0
        elif travel_mode in ["car", "bus"]:
            budget["transport"] = days * 800.0
        
        # Calculate total
        total = sum(v for k, v in budget.items() if k != "currency" and isinstance(v, (int, float)))
        budget["total"] = total
        
        return schemas.Budget(**budget)

    async def _fetch_attractions(self, location_data):
        """Helper to fetch attractions"""
        attractions_list = []
        try:
            lat = location_data.get("lat")
            lon = location_data.get("lon")
            if lat and lon:
                places_data = await geoapify_service.get_places(
                    lat=lat, lon=lon, categories="tourism", radius=10000, limit=15
                )
                for place in places_data:
                    desc = place.get("description")
                    if isinstance(desc, list):
                        desc = ", ".join(desc) if desc else None
                    attractions_list.append(schemas.Attraction(
                        name=place.get("name"),
                        kind=place.get("kind"),
                        description=desc,
                        image=place.get("image"),
                        wikipedia_url=place.get("wikipedia_url"),
                        coordinates=schemas.Coordinates(
                            latitude=place.get("latitude"),
                            longitude=place.get("longitude")
                        ) if place.get("latitude") and place.get("longitude") else None
                    ))
        except Exception as e:
            logger.error(f"Error fetching attractions: {e}")
        return attractions_list

    def _fetch_travel_info(self, destination_name, origin_code, travel_date):
        """Helper to fetch flight and airport info"""
        nearby_airports = []
        flight_offers = []
        try:
            if origin_code and travel_date:
                flight_result = travel_service.search_flights(
                    origin=origin_code, destination=destination_name, departure_date=travel_date
                )
                if "flights" in flight_result and isinstance(flight_result["flights"], list):
                    for offer in flight_result["flights"][:3]:
                        price = offer.get("price", {})
                        itineraries = offer.get("itineraries", [])
                        if itineraries:
                            segments = itineraries[0].get("segments", [])
                            first_seg = segments[0]
                            last_seg = segments[-1]
                            flight_offers.append(schemas.FlightOffer(
                                price=str(price.get("total")),
                                currency=price.get("currency", "INR"),
                                airline=first_seg.get("airlineName", first_seg.get("carrierCode")),
                                departure=first_seg.get("departure", {}).get("at"),
                                arrival=last_seg.get("arrival", {}).get("at"),
                                duration=itineraries[0].get("duration")
                            ))
            
            loc_results = travel_service.search_locations(destination_name)
            if isinstance(loc_results, list):
                for loc in loc_results:
                    if loc.get("subType") in ["AIRPORT", "CITY"]:
                        nearby_airports.append({
                            "name": loc.get("name"),
                            "iataCode": loc.get("iataCode"),
                            "subType": loc.get("subType")
                        })
        except Exception:
            pass 
        return nearby_airports, flight_offers

    def _generate_recommendations(self, attractions, flights, days):
        recommendations = []
        if attractions:
            recommendations.append(f"Must visit: {attractions[0].name}")
        if flights:
            recommendations.append(f"Best flight price: {flights[0].price} {flights[0].currency}")
        if days > 3:
            recommendations.append(f"Consider booking accommodation in advance for {days}-day trip")
        return recommendations

    async def _generate_multi_city_plan(
        self, destinations: List[str], origin, start_date, total_days, travel_mode
    ) -> schemas.TravelPlanResponse:
        """Handle multi-destination itinerary generation"""
        from datetime import datetime
        import datetime as dt_module
        
        # 1. Geocode all destinations
        city_data_list = []
        all_attractions = []
        
        for city in destinations:
            loc = await geoapify_service.forward_geocoding(city)
            if loc:
                attrs = await self._fetch_attractions(loc)
                city_data_list.append({"location": loc, "attractions": attrs})
                all_attractions.extend(attrs)
        
        if not city_data_list:
            raise ValueError("No valid destinations found.")

        # 2. Distribute Days
        num_cities = len(city_data_list)
        base_days = max(1, total_days // num_cities)
        remainder = total_days % num_cities
        
        # 3. Generate Itinerary Chain
        full_itinerary = []
        current_day_num = 1
        current_date_str = start_date
        
        prev_city_name = origin if origin else "Origin"
        
        for i, data in enumerate(city_data_list):
            city_name = data["location"]["name"]
            city_attractions = data["attractions"]
            
            # Allocate days for this city
            days_in_city = base_days + (1 if i < remainder else 0)
            
            # Generate days for this city
            for d in range(days_in_city):
                activities = []
                
                # TRANSIT ACTIVITY (Only on first day in city)
                if d == 0:
                    transit_note = f"Travel from {prev_city_name} to {city_name}"
                    if i == 0 and origin: 
                         transit_note = f"{travel_mode.title()} from {origin} to {city_name}"
                    
                    activities.append(schemas.Activity(
                        time="08:00",
                        attraction=schemas.Attraction(
                            name=f"Travel: {prev_city_name} → {city_name}",
                            kind="travel", description=transit_note
                        ),
                        duration_hours=4.0,
                        notes=transit_note
                    ))
                
                # SIGHTSEEING ACTIVITIES
                attr_per_day = 3
                start_idx = d * attr_per_day
                day_attractions = city_attractions[start_idx : start_idx + attr_per_day]
                
                curr_hour = 13 if d == 0 else 9 
                
                for attr in day_attractions:
                    activities.append(schemas.Activity(
                        time=f"{curr_hour:02d}:00",
                        attraction=attr,
                        duration_hours=1.5,
                        notes=f"Explore {attr.name}"
                    ))
                    curr_hour += 2
                
                full_itinerary.append(schemas.DayItinerary(
                    day_number=current_day_num,
                    date=current_date_str,
                    activities=activities,
                    meals=[f"Breakfast in {prev_city_name if d==0 else city_name}", f"Dinner in {city_name}"],
                    accommodation=f"Hotel in {city_name}"
                ))
                
                # Increment date
                if current_date_str:
                    try:
                        dt = datetime.strptime(current_date_str, "%Y-%m-%d")
                        current_date_str = (dt + dt_module.timedelta(days=1)).strftime("%Y-%m-%d")
                    except: pass
                
                current_day_num += 1
            
            prev_city_name = city_name

        # 4. Final Return Journey
        if full_itinerary and origin:
            last_day = full_itinerary[-1]
            last_day.activities.append(schemas.Activity(
                time="16:00",
                attraction=schemas.Attraction(
                    name=f"Return: {prev_city_name} → {origin}",
                    kind="travel", description="Return journey home"
                ),
                duration_hours=4.0,
                notes=f"Return journey to {origin}"
            ))
            last_day.accommodation = None 

        main_dest = city_data_list[0]["location"]
        dest_details = schemas.DestinationDetails(
             name=main_dest.get("name"), country=main_dest.get("country"),
             coordinates=schemas.Coordinates(latitude=main_dest.get("lat"), longitude=main_dest.get("lon"))
        )
        
        return schemas.TravelPlanResponse(
            destination=dest_details,
            attractions=all_attractions,
            itinerary=full_itinerary,
            travel_mode=travel_mode,
            total_days=total_days,
            estimated_budget=self._calculate_budget(total_days, [], travel_mode),
            recommendations=["Enjoy your multi-city road trip!"]
        )

# Global Instance
orchestrator_service = OrchestratorService()
