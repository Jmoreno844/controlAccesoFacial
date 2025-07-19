import sys
import os
from fastapi import FastAPI

# Add the current directory to the path to ensure modules are found
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import session, models

# Create the database tables
models.Base.metadata.create_all(bind=session.engine)

app = FastAPI(title="Facial Access Control API")

# Import and mount the API app after creating the main app
from api.api import app as api_app
app.mount("/api", api_app)

@app.middleware("http")
async def log_requests(request, call_next):
    print(f"→ {request.method} {request.url}")
    return await call_next(request)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Facial Access Control API"}