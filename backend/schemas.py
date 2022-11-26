from pydantic import BaseModel, EmailStr
from typing import List
from datetime import datetime

# Models for JSON input/output data validation. See models.py for SQLAlchemy models for DB.

class OrmModel(BaseModel):
    class Config():
        orm_mode = True

class User(OrmModel):
    username: str
    email: EmailStr
    role: str
    
class UserCreate(User):
    password: str

class UserRead(User):
    created_at: datetime

class UserReadAdmin(UserRead):
    id: int