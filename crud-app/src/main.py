import logging
import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager

from src import models
from src.database import engine
from src.database import engine
from src.routers import users, travel
from config.settings import settings

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create tables on startup
models.Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up application...")
    yield
    logger.info("Shutting down application...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    lifespan=lifespan
)

app.include_router(users.router, prefix="/api", tags=["users"])
app.include_router(travel.router, prefix="/api/travel", tags=["travel"])

@app.get("/")
def root():
    return {"message": "Welcome to the FastAPI CRUD Application. Visit /docs for Swagger UI."}

if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
