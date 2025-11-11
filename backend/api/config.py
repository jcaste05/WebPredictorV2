import os
from datetime import timedelta

# Define json encoding and token creation settings
SECRET_KEY = os.getenv("API_HOST_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
def access_token_timedelta() -> timedelta:
    return timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

# Define IP key salt for rate limiting
IP_KEY_SALT = os.getenv("IP_KEY_SALT")

# Define Redis database URL
REDIS_URL = os.getenv("REDIS_URL")

# DEFINE RATE LIMITING SETTINGS
DEFAULT_RL = (10, 60) # DEFAULT_RL[0] requests per DEFAULT_RL[1] seconds

# Define available scopes and implications
SCOPES: dict[str, str] = {
    "admin": "Administrative privileged operations",
    "client": "Client operations",
}
SCOPE_IMPLICATIONS: dict[str, set[str]] = {
    "admin": {"client"},
}
