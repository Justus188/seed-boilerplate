from pydantic import BaseModel, EmailStr
from typing import List
from datetime import datetime

# Models for JSON input/output data validation. See models.py for SQLAlchemy models for DB.

class ErrorDetailChildMsg(BaseModel):
    msg: str

class ErrorDetailChildMsgLoc(ErrorDetailChildMsg):
    loc: List[str]

class ErrorDetailChildMsgLocType(ErrorDetailChildMsgLoc):
    type: str

class ErrorDetailFlat(BaseModel):
    detail: str

class ErrorDetailParentMsg(BaseModel):
    detail: ErrorDetailChildMsg

class ErrorDetailLocParent(BaseModel):
    detail: ErrorDetailChildMsgLoc

class ErrorDetailLocTypeParent(BaseModel):
    detail: ErrorDetailChildMsgLocType

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
    id: int

class UserUpdate(OrmModel):
    username: str|None = None
    email: EmailStr|None = None
    password: str|None = None
    role: str|None = None