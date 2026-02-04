from sqlalchemy import Column, Integer, String, TIMESTAMP, func
from src.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    def __repr__(self):
        return f"<User(id={self.id}, name='{self.name}', email='{self.email}')>"
