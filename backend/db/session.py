import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# File-based SQLite for local dev
USERS_DB_URL = os.getenv("USERS_DB_URL")

if "sqlite://" in USERS_DB_URL:
    print("INFO: Using SQLite database for users.")
    engine = create_engine(
        USERS_DB_URL,
        connect_args={
            "check_same_thread": False
        },  # Needed for SQLite with multithreaded ASGI
    )
elif "postgres" in USERS_DB_URL:
    print("INFO: Using PostgreSQL database for users.")
    if USERS_DB_URL and USERS_DB_URL.startswith("postgresql://"):
        USERS_DB_URL = USERS_DB_URL.replace("postgresql://", "postgresql+psycopg://", 1)
    engine = create_engine(USERS_DB_URL, pool_pre_ping=True)

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
