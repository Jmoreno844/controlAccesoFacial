import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .session import Base

class User(Base):
    """User model for storing user information."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True)  # For admin password
    role = Column(String, default="user", nullable=False)  # "user" or "admin"
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    rfid_card_id = Column(String, unique=True, index=True, nullable=True)
    logs = relationship("Log", back_populates="user")

class Log(Base):
    """Log model for recording access events."""
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Nullable for unknown faces
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    event_type = Column(String, nullable=False)  # e.g., 'login_success', 'login_failure'
    details = Column(String, nullable=True)  # e.g., 'Rostro no conocido'

    user = relationship("User", back_populates="logs")
