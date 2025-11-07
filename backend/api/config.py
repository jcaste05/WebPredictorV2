import os
from datetime import timedelta

SECRET_KEY = os.getenv("API_HOST_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
def access_token_timedelta() -> timedelta:
    return timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

USERS_DB_URL = os.getenv("USERS_DB_URL")

SCOPES: dict[str, str] = {
    "admin": "Administrative privileged operations",
    "client": "Client operations",
}
SCOPE_IMPLICATIONS: dict[str, set[str]] = {
    "admin": {"client"},
}
