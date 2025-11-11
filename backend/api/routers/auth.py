from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_limiter.depends import RateLimiter

from backend.api.config import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    DEFAULT_RL,
    SCOPE_IMPLICATIONS,
    SCOPES,
)
from backend.api.schemas.auth_schemas import ScopesResponse, TokenResponse
from backend.api.security.auth import authenticate_user, create_access_token

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    dependencies=[
        Depends(RateLimiter(times=DEFAULT_RL[0], seconds=DEFAULT_RL[1])),
    ],
)

login_kwargs = dict(
    response_model=TokenResponse,
    summary="Obtain JWT access token (accepts form url encoded)",
)


@router.post("/login", **login_kwargs)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    username = form_data.username
    password = form_data.password
    scopes = list(form_data.scopes)

    user = authenticate_user(username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    granted_scopes: list[str] = []
    for scope in scopes:
        if scope == user.role or scope in SCOPE_IMPLICATIONS.get(user.role, []):
            granted_scopes.append(scope)
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient role for '{scope}' scope",
            )
    if len(granted_scopes) == 0:
        granted_scopes.append(user.role)

    token = create_access_token(username, scopes=granted_scopes)
    return TokenResponse(
        access_token=token,
        expires_minutes=ACCESS_TOKEN_EXPIRE_MINUTES,
        scopes=granted_scopes,
    )


scopes_kwargs = dict(
    response_model=ScopesResponse,
    summary="Available scopes and descriptions",
)


@router.get("/scopes", **scopes_kwargs)
def get_scopes():
    return ScopesResponse(scopes=SCOPES)
