from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
import logging

from database import models, session
from database.crud import user_crud, logs_crud
from . import schemas
from fastapi import Body

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables
models.Base.metadata.create_all(bind=session.engine)

app = FastAPI(title="Access Control API")

# --- Dependency ---
def get_db():
    db = session.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Test Endpoint ---

@app.post("/test", tags=["Test"])
def test_endpoint(data: dict):
    """Test endpoint that accepts JSON with id field and prints it"""
    print(f"Received test data: {data}")
    if "id" in data:
        print(f"ID: {data['id']}")
    else:
        print("No ID field found in data")
    return {"message": "Test successful", "received_data": data}

# --- User Endpoints ---

@app.post("/users/", response_model=schemas.User, tags=["Users"])
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    logger.info(f"Received POST request to create user: {user.name}")
    # Check if a user with the same name already exists
    db_user = user_crud.get_user_by_name(db, name=user.name)
    if db_user:
        raise HTTPException(status_code=400, detail="User with this name already registered")
    return user_crud.create_user(db=db, user=user)

@app.get("/users/", response_model=List[schemas.User], tags=["Users"])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = user_crud.get_users(db, skip=skip, limit=limit)
    return users

@app.get("/users/{user_id}", response_model=schemas.User, tags=["Users"])
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = user_crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.get("/users/name/{user_name}", response_model=schemas.User, tags=["Users"])
def read_user_by_name(user_name: str, db: Session = Depends(get_db)):
    """Retrieve a user by their name."""
    db_user = user_crud.get_user_by_name(db, name=user_name)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

# --- Admin Endpoints ---

@app.post("/admin/login", tags=["Admin"])
def admin_login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Logs in an admin user by checking credentials."""
    user = user_crud.get_user_by_name(db, name=form_data.username)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials or not an admin")

    # Retrieve role and hashed password to avoid SQLAlchemy InstrumentedAttribute
    user_role = getattr(user, 'role', None)
    if user_role != 'admin':
        raise HTTPException(status_code=401, detail="Invalid credentials or not an admin")

    hashed_pw = getattr(user, 'hashed_password', None)
    if not hashed_pw:
        raise HTTPException(status_code=401, detail="Invalid credentials or not an admin")

    if not user_crud.PasswordHasher.verify_password(form_data.password, hashed_pw):
        raise HTTPException(status_code=401, detail="Invalid credentials or not an admin")

    return {"message": "Admin login successful", "username": user.name}


# --- Log Endpoints ---

@app.post("/logs/", response_model=schemas.Log, tags=["Logs"])
def create_log(log: schemas.LogCreate, db: Session = Depends(get_db)):
    return logs_crud.create_log(db=db, log=log)

@app.get("/logs/", response_model=List[schemas.Log], tags=["Logs"])
def read_logs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    logs = logs_crud.get_logs(db, skip=skip, limit=limit)
    return logs

# --- RFID Card Scan Log Endpoint ---
@app.post("/logs/rfid_card", response_model=schemas.Log, tags=["Logs"])
def log_rfid_card(request: schemas.RfidCardRequest, db: Session = Depends(get_db)):
    """Check RFID card and create a success or error log."""
    # Find user by RFID card ID
    user = user_crud.get_user_by_rfid(db, rfid_card_id=request.id)
    if user:
        user_id_val = getattr(user, 'id', None)
        log_entry = schemas.LogCreate(event_type="rfid_success", details=f"rfid_success -- User: {user.name}", user_id=user_id_val)
    else:
        log_entry = schemas.LogCreate(event_type="rfid_error", details="rfid error", user_id=None)
    return logs_crud.create_log(db=db, log=log_entry)

# --- Update User RFID Endpoint ---
@app.put("/users/{user_id}", response_model=schemas.User, tags=["Users"])
def update_user_rfid(
    user_id: int,
    update: schemas.UserUpdate = Body(...),
    db: Session = Depends(get_db)
):
    """Update a user's RFID card."""
    db_user = user_crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if update.rfid_card_id is not None:
        setattr(db_user, 'rfid_card_id', update.rfid_card_id)
    db.commit()
    db.refresh(db_user)
    return db_user
