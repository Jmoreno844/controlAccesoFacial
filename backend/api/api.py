from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import models, session
from database.crud import user_crud, logs_crud
from . import schemas

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

# --- User Endpoints ---

@app.post("/users/", response_model=schemas.User, tags=["Users"])
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = user_crud.get_user_by_user_code(db, user_code=user.user_code)
    if db_user:
        raise HTTPException(status_code=400, detail="User code already registered")
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

# --- Log Endpoints ---

@app.post("/logs/", response_model=schemas.Log, tags=["Logs"])
def create_log(log: schemas.LogCreate, db: Session = Depends(get_db)):
    return logs_crud.create_log(db=db, log=log)

@app.get("/logs/", response_model=List[schemas.Log], tags=["Logs"])
def read_logs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    logs = logs_crud.get_logs(db, skip=skip, limit=limit)
    return logs
