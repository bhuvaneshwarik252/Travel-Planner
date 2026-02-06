import asyncio
import logging
from src.services.travel_service import travel_service

# Setup logging
logging.basicConfig(level=logging.INFO)

def test_search():
    variations = ["bengalore", "Bangalore", "Bengaluru", "BLR"]
    
    for origin in variations:
        print(f"\n--- Resolving Origin: '{origin}' ---")
        origin_loc = travel_service._resolve_location(origin)
        print(f"Result: {origin_loc}")

if __name__ == "__main__":
    test_search()
