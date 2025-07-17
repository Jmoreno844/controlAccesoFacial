from sqlalchemy.orm import Session
from database import models
from api import schemas

def get_user(db: Session, user_id: int):
    """Retrieve a single user by their ID."""
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_user_code(db: Session, user_code: str):
    """Retrieve a single user by their user_code."""
    return db.query(models.User).filter(models.User.user_code == user_code).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    """Retrieve a list of users with pagination."""
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    """Create a new user in the database."""
    db_user = models.User(
        user_code=user.user_code,
        name=user.name,
        rfid_card_id=user.rfid_card_id
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
