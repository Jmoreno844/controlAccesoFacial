import getpass
from sqlalchemy.orm import Session
from database.session import SessionLocal, engine
from database.models import User, Base
from database.crud.user_crud import create_user
from api.schemas import UserCreate

def create_admin_user(db: Session, name: str, password: str):
    """Creates an admin user."""
    admin_user = UserCreate(name=name, password=password, role='admin')
    create_user(db=db, user=admin_user)
    print(f"Admin user '{name}' created successfully.")

def main():
    Base.metadata.create_all(bind=engine)
    
    name = input("Enter admin username: ")
    password = getpass.getpass("Enter admin password: ")
    password_confirm = getpass.getpass("Confirm admin password: ")

    if password != password_confirm:
        print("Passwords do not match.")
        return

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.name == name).first()
        if user:
            print(f"User with name '{name}' already exists.")
            return
        create_admin_user(db, name, password)
    finally:
        db.close()

if __name__ == "__main__":
    main() 