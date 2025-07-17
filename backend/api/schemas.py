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
    user_code: str
    name: str
    rfid_card_id: Optional[str] = None

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int
    created_at: datetime.datetime
    logs: List[Log] = []

    class Config:
        orm_mode = True
