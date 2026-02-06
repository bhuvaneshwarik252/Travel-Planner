from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import List
from jose import JWTError, jwt

from src import crud, schemas, models
from src.database import get_db
from config.settings import settings

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/users/login")

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    return user

@router.post("/trips", response_model=schemas.TripResponse)
def create_trip(trip: schemas.TripCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return crud.create_trip(db=db, trip=trip, user_id=current_user.id)

@router.get("/trips", response_model=List[schemas.TripResponse])
def read_trips(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return crud.get_trips(db=db, user_id=current_user.id)

@router.delete("/trips/{trip_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_trip(trip_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    success = crud.delete_trip(db=db, trip_id=trip_id, user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
    return None
