from amadeus import Client, ResponseError
from config.settings import settings
import logging

# Setup logging to see output
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_amadeus():
    print("-" * 20)
    print(f"CLIENT_ID: {settings.AMADEUS_CLIENT_ID}")
    print(f"CLIENT_SECRET: {settings.AMADEUS_CLIENT_SECRET}") # Be careful not to leak full secret if real, but here we need to debug.
    print("-" * 20)

    if not settings.AMADEUS_CLIENT_ID or not settings.AMADEUS_CLIENT_SECRET:
        print("ERROR: Credentials missing in settings.")
        return

    try:
        client = Client(
            client_id=settings.AMADEUS_CLIENT_ID,
            client_secret=settings.AMADEUS_CLIENT_SECRET,
            log_level='debug' # Enable debug logs for Amadeus
        )
        print("Client initialized. Attempting to fetch token...")
        
        # Explicitly request token to test auth
        token = client.session.get_token()
        print(f"SUCCESS! Token received: {token}")
        
    except ResponseError as error:
        print(f"AMADEUS API ERROR: {error}")
        print(f"Code: {error.code}")
        print(f"Description: {error.description}")
        if error.response:
            print(f"Response Body: {error.response.body}")
    except Exception as e:
        print(f"GENERAL ERROR: {e}")

if __name__ == "__main__":
    test_amadeus()
