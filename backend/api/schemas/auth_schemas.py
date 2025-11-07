from pydantic import BaseModel


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_minutes: int
    scopes: list[str]


class ScopesResponse(BaseModel):
    scopes: dict[str, str]
