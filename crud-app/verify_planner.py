import requests
import json
import sys

def verify_planner_structure():
    url = "http://127.0.0.1:8000/api/plan"
    params = {
        "destination": "Paris",
        "days": 1,
        "travel_mode": "flight"
    }
    
    try:
        print(f"Requesting {url} with params {params}...")
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        print("\n--- API Response Structure Analysis ---")
        if "itinerary" in data and data["itinerary"]:
            day1 = data["itinerary"][0]
            if "activities" in day1 and day1["activities"]:
                act = day1["activities"][0]
                print(f"Activity Keys: {list(act.keys())}")
                
                if "attraction" in act:
                    attr = act["attraction"]
                    print(f"Attraction Keys: {list(attr.keys())}")
                    print(f"Attraction Name: {attr.get('name')}")
                    
                    if attr.get("name"):
                        print("\nSUCCESS: 'attraction.name' is accessible.")
                    else:
                        print("\nFAILURE: 'attraction.name' is missing or empty.")
                else:
                    print("\nFAILURE: 'attraction' key missing in activity.")
            else:
                print("No activities found in day 1.")
        else:
            print("No itinerary returned.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify_planner_structure()
