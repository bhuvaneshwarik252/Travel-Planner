import logging
import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from src import models
from src.database import engine
from src.routers import users, travel, health, planner, trips
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

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(users.router, prefix="/api", tags=["users"])
app.include_router(trips.router, prefix="/api", tags=["trips"])
app.include_router(travel.router, prefix="/api/travel", tags=["travel"])
app.include_router(health.router)
app.include_router(planner.router, prefix="/api", tags=["planner"])

@app.get("/")
def root():
    return FileResponse('static/index.html')

@app.get("/dashboard")
def dashboard():
    return FileResponse('static/dashboard.html')

if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
