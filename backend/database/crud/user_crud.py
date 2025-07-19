from sqlalchemy.orm import Session
from passlib.context import CryptContext
from database import models
from api import schemas

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class PasswordHasher:
    @staticmethod
    def verify_password(plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password):
        return pwd_context.hash(password)

def get_user(db: Session, user_id: int):
    """Retrieve a single user by their ID."""
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_name(db: Session, name: str):
    """Retrieve a single user by their name."""
    return db.query(models.User).filter(models.User.name == name).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    """Retrieve a list of users with pagination."""
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    """Create a new user in the database."""
    hashed_password = None
    if user.password:
        hashed_password = PasswordHasher.get_password_hash(user.password)
    
    db_user = models.User(
        name=user.name,
        rfid_card_id=user.rfid_card_id,
        hashed_password=hashed_password,
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_rfid(db: Session, rfid_card_id: str):
    """Retrieve a single user by their RFID card ID."""
    return db.query(models.User).filter(models.User.rfid_card_id == rfid_card_id).first()
