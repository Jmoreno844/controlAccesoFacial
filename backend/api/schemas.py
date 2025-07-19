from pydantic import BaseModel
import datetime
from typing import Optional, List

# --- Log Schemas ---

class LogBase(BaseModel):
    event_type: str
    details: Optional[str] = None
    user_id: Optional[int] = None

class LogCreate(LogBase):
    pass

class Log(LogBase):
    id: int
    timestamp: datetime.datetime

    class Config:
        orm_mode = True

# --- User Schemas ---

class UserBase(BaseModel):
    name: str
    rfid_card_id: Optional[str] = None
    role: str = "user"

class UserCreate(UserBase):
    password: Optional[str] = None

class UserUpdate(BaseModel):
    rfid_card_id: Optional[str] = None

class RfidCardRequest(BaseModel):
    id: str

class User(UserBase):
    id: int
    created_at: datetime.datetime
    logs: List[Log] = []

    class Config:
        orm_mode = True
