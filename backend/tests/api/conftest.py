import os
from unittest.mock import AsyncMock, patch

# Ensure DB URL exists before importing backend code
os.environ.setdefault("USERS_DB_URL", "sqlite:///./users_test.db")
os.environ.setdefault("REDIS_URL", "redis://fake:6379/0")
os.environ.setdefault("API_HOST_SECRET_KEY", "test-secret-key-for-testing-only")
os.environ.setdefault("IP_KEY_SALT", "test-salt-for-ip-hashing")


import pytest
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def mock_redis():
    """Mock Redis dependencies globally for all tests."""
    print("PyTest: Setting up mock_redis fixture")
    # Create a mock Redis client
    mock_redis_client = AsyncMock()
    mock_redis_client.ping.return_value = True
    mock_redis_client.close.return_value = None
    mock_redis_client.flushall.return_value = None

    # Mock redis.asyncio.from_url to return our mock client
    with patch("redis.asyncio.from_url", return_value=mock_redis_client):
        # Mock FastAPILimiter.init to do nothing
        with patch("fastapi_limiter.FastAPILimiter.init", return_value=None):
            # Mock the RateLimiter dependency to always pass
            with patch("fastapi_limiter.depends.RateLimiter") as mock_rate_limiter:
                # Return a function that does nothing (no rate limiting)
                mock_rate_limiter.return_value = lambda: None
                yield


@pytest.fixture
def client():
    print("PyTest: Setting up client fixture")
    """Test client with all dependencies mocked."""
    from backend.api.main import app

    return TestClient(app)
