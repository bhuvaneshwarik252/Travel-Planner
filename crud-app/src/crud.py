from sqlalchemy.orm import Session
from src import models, schemas
from src.auth import get_password_hash

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(name=user.name, email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate):
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    update_data = user_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user, key, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int):
    db_user = get_user(db, user_id)
    if db_user:
        db.delete(db_user)
        db.commit()
    return False

def create_trip(db: Session, trip: schemas.TripCreate, user_id: int):
    # Serialize itinerary to string if it's not already
    import json
    if not isinstance(trip.itinerary, str):
        trip.itinerary = json.dumps(trip.itinerary)
        
    db_trip = models.Trip(**trip.model_dump(), user_id=user_id)
    db.add(db_trip)
    db.commit()
    db.refresh(db_trip)
    return db_trip

def get_trips(db: Session, user_id: int):
    return db.query(models.Trip).filter(models.Trip.user_id == user_id).all()

def delete_trip(db: Session, trip_id: int, user_id: int):
    trip = db.query(models.Trip).filter(models.Trip.id == trip_id, models.Trip.user_id == user_id).first()
    if trip:
        db.delete(trip)
        db.commit()
        return True
    return False
