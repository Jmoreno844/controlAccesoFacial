import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Define the path for the database file inside a 'data' directory
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
db_dir = os.path.join(project_root, 'data')
if not os.path.exists(db_dir):
    os.makedirs(db_dir)

DATABASE_URL = f"sqlite:///{os.path.join(db_dir, 'access_control.db')}"

engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False}  # Needed for SQLite in a multi-threaded context
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Generator function to get a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
