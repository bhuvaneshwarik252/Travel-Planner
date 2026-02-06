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

    # Geoapify Settings
    GEOAPIFY_API_KEY: str = os.getenv("GEOAPIFY_API_KEY", "")

    # Unsplash Settings
    UNSPLASH_ACCESS_KEY: str = os.getenv("UNSPLASH_ACCESS_KEY", "")

    # Auth Settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

settings = Settings()
