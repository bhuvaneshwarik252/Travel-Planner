from amadeus import Client
from config.settings import settings
import logging

def test_amadeus():
    try:
        client = Client(
            client_id=settings.AMADEUS_CLIENT_ID,
            client_secret=settings.AMADEUS_CLIENT_SECRET,
        )
        print("Client dir:", dir(client))
        
        # Try to find where access token is
        if hasattr(client, 'auth'):
             print("Client.auth dir:", dir(client.auth))
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_amadeus()
