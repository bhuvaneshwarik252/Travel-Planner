from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from src.services.orchestrator import orchestrator_service
from src import schemas
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/plan", response_model=schemas.TravelPlanResponse, tags=["planner"])
async def get_travel_plan(
    destination: str = Query(..., min_length=2, description="Target destination (e.g., Paris, London)"),
    origin: Optional[str] = Query(None, min_length=3, description="Origin Name (e.g., London) or IATA code (e.g., LHR)"),
    date: Optional[str] = Query(None, description="Date of travel (YYYY-MM-DD)")
):
    """
    **Intelligent Travel Planner**
    
    Generates a comprehensive travel plan by orchestrating data from multiple sources:
    - **GeoDB**: City details and demographics.
    - **OpenTripMap**: Tourist attractions and points of interest.
    - **Amadeus**: Flight offers and airport information.
    
    Returns a unified response with destination context, sights to see, and travel options.
    """
    try:
        plan = await orchestrator_service.generate_travel_plan(
            destination_name=destination, 
            origin_code=origin, 
            travel_date=date
        )
        return plan
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Internal Orchestration Error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Error: {str(e)}")
