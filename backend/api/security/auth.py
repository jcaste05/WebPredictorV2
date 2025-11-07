from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jose import JWTError, jwt
from passlib.context import CryptContext

from backend.api.config import (
    ALGORITHM,
    SCOPES,
    SCOPE_IMPLICATIONS,
    SECRET_KEY,
    access_token_timedelta,
)
from backend.db.models import User
from backend.db.session import SessionLocal

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login",
    scopes=SCOPES,
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _get_user(username: str) -> User | None:
    db = SessionLocal()
    try:
        row = db.query(User).filter(User.user == username).first()
        return row
    finally:
        db.close()


def _verify_password(password: str, stored_hash: str | None) -> bool:
    if stored_hash is None:
        return False
    return pwd_context.verify(password, stored_hash)


def authenticate_user(username: str, password: str) -> User | None:
    user = _get_user(username)
    if user and _verify_password(password, user.password):
        return user
    return None


def create_access_token(
    subject: str, scopes: list[str], expires_delta: Optional[timedelta] = None
) -> str:
    if expires_delta is None:
        expires_delta = access_token_timedelta()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {"sub": subject, "exp": expire, "scopes": scopes}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
    security_scopes: SecurityScopes, token: str = Depends(oauth2_scheme)
) -> User:
    authenticate_value = (
        f'Bearer scope="{security_scopes.scope_str}"'
        if security_scopes.scopes
        else "Bearer"
    )
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token",
        headers={"WWW-Authenticate": authenticate_value},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        token_scopes: list[str] = payload.get("scopes", [])
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Verify required scopes
    effective_scopes = set(token_scopes)
    for s in token_scopes:
        implied = SCOPE_IMPLICATIONS.get(s)
        if implied:
            effective_scopes.update(implied)

    for required in security_scopes.scopes:
        if required not in effective_scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient scope. Missing: {required}",
                headers={"WWW-Authenticate": authenticate_value},
            )

    # Return user
    user = _get_user(username)
    if user is None:
        raise credentials_exception
    return user
