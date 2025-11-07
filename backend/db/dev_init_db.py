import os

from passlib.context import CryptContext

from backend.db.models import User
from backend.db.session import Base, SessionLocal, engine

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def init_db():
    """Create all tables. Idempotent."""
    Base.metadata.create_all(bind=engine)


def create_user(user: str, password: str, role: str = "user"):
    db = SessionLocal()
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.user == user).first()
        if existing_user:
            return None

        # Create new user
        new_user = User(user=user, password=pwd_context.hash(password), role=role)
        db.add(new_user)
        db.commit()  # Save to DB
        db.refresh(new_user)  # Refresh database object
        return new_user
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
    # Create default admin user (requires ADMIN_PASSWORD env var)
    new_admin = create_user("admin", os.getenv("ADMIN_PASSWORD"), role="admin")
    if new_admin:
        print(
            f"Admin user created: user = {new_admin.user}, id = {new_admin.id}, role = {new_admin.role}"
        )
    else:
        print("Admin user already exists.")
