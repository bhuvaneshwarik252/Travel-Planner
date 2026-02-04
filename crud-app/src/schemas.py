from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

# Shared properties
class UserBase(BaseModel):
    name: str
    email: EmailStr

# Properties to receive via API on creation
class UserCreate(UserBase):
    pass

# Properties to receive via API on update (all optional)
class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None

# Properties to return to client
class UserResponse(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
