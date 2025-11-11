from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi_limiter.depends import RateLimiter
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from backend.api.config import DEFAULT_RL
from backend.api.schemas.admin_schemas import UserCreate, UserId, UserOut
from backend.api.security.auth import get_current_user
from backend.db.models import User
from backend.db.session import get_db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[
        Security(get_current_user, scopes=["admin"]),
        Depends(RateLimiter(times=DEFAULT_RL[0], seconds=DEFAULT_RL[1])),
    ],
)


@router.post("/create_user", response_model=UserOut, summary="Create a new user")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.user == user.user).first()
    if existing:
        raise HTTPException(status_code=409, detail="User already exists")

    pwd_plain = user.password
    pwd_hash = pwd_context.hash(pwd_plain)
    data = dict(user=user.user, password=pwd_hash, role=user.role)
    db_obj = User(**data)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return UserOut(id=db_obj.id, user=db_obj.user, role=db_obj.role)


@router.post("/delete_user", response_model=UserOut, summary="Delete a user")
def delete_user(user_id: UserId, db: Session = Depends(get_db)):
    if user_id.id is not None:
        r = db.query(User).filter_by(id=user_id.id).first()
    elif user_id.user is not None:
        r = db.query(User).filter_by(user=user_id.user).first()
    else:
        raise HTTPException(status_code=400, detail="Invalid user identifier")

    if not r:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(r)
    db.commit()
    return UserOut(id=r.id, user=r.user, role=r.role)


change_password_kwargs = dict(
    response_model=UserOut,
    summary="Change user password and role (optional)",
)


@router.post("/change_password", **change_password_kwargs)
def change_password(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.user == user.user).first()
    if not existing:
        raise HTTPException(status_code=404, detail="User not found")
    existing.password = pwd_context.hash(user.password)
    if user.role and user.role != existing.role:
        existing.role = user.role
    db.commit()
    db.refresh(existing)
    return UserOut(id=existing.id, user=existing.user, role=existing.role)


@router.get("/", response_model=list[UserOut], summary="List all users")
def list_users(db: Session = Depends(get_db)):
    rows = db.query(User).all()
    return [{"id": r.id, "user": r.user, "role": r.role} for r in rows]


@router.post("/get_user", response_model=UserOut, summary="Get user by id or user")
def get_user(user_id: UserId, db: Session = Depends(get_db)):
    if user_id.id is not None:
        r = db.query(User).filter_by(id=user_id.id).first()
    elif user_id.user is not None:
        r = db.query(User).filter_by(user=user_id.user).first()
    else:
        raise HTTPException(status_code=400, detail="Invalid user identifier")

    if not r:
        raise HTTPException(status_code=404, detail="User not found")
    return UserOut(id=r.id, user=r.user, role=r.role)
