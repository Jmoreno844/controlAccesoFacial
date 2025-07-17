from sqlalchemy.orm import Session
from database import models
from api import schemas

def create_log(db: Session, log: schemas.LogCreate):
    """Create a new log entry in the database."""
    db_log = models.Log(**log.dict())
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

def get_logs(db: Session, skip: int = 0, limit: int = 100):
    """Retrieve a list of logs with pagination."""
    return db.query(models.Log).order_by(models.Log.timestamp.desc()).offset(skip).limit(limit).all()
