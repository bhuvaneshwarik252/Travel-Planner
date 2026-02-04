from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config.settings import settings
import os

# Ensure the database directory exists
db_path = settings.DATABASE_URL.replace("sqlite:///", "")
if ":memory:" not in db_path:
    # If using a relative path like ./db/crud_db.sqlite, we need to make sure db/ exists
    # relative to where we run the app. However, settings usually resolves absolute or relative.
    # For a simple SQLite file, we'll strip the prefix and check the directory.
    os.makedirs(os.path.dirname(os.path.abspath(db_path)) if os.path.dirname(db_path) else "db", exist_ok=True)

# connect_args={"check_same_thread": False} is required for SQLite
engine = create_engine(
    settings.DATABASE_URL, 
    connect_args={"check_same_thread": False},
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
