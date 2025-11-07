import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# File-based SQLite for local dev
USERS_DB_URL = os.getenv("USERS_DB_URL", "sqlite:///./users.db")

engine = create_engine(
    USERS_DB_URL,
    connect_args={"check_same_thread": False},  # Needed for SQLite with multithreaded ASGI
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """Declarative base class for ORM models."""
    pass


def get_db():
    """FastAPI dependency that provides a DB session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
