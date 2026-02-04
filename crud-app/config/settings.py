import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_path)

class Settings:
    PROJECT_NAME: str = os.getenv("APP_NAME", "FastAPI CRUD Service")
    PROJECT_VERSION: str = "1.0.0"
    
    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./db/crud_db.sqlite")
    
    # API Settings
    API_V1_STR: str = "/api/v1"

    # Amadeus API Settings
    AMADEUS_CLIENT_ID: str = os.getenv("AMADEUS_CLIENT_ID", "")
    AMADEUS_CLIENT_SECRET: str = os.getenv("AMADEUS_CLIENT_SECRET", "")

    # OpenTripMap Settings
    OPENTRIPMAP_API_KEY: str = os.getenv("OPENTRIPMAP_API_KEY", "")

    # GeoDB Cities Settings
    GEODB_API_KEY: str = os.getenv("GEODB_API_KEY", "")
    GEODB_API_HOST: str = os.getenv("GEODB_API_HOST", "wft-geo-db.p.rapidapi.com")

settings = Settings()
