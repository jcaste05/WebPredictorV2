from backend.db.dev_init_db import create_user, init_db

ADMIN_USER = "admin"
ADMIN_PASS = "adminpass"
CLIENT_USER = "client"
CLIENT_PASS = "clientpass"


def _ensure_users_created():
    init_db()
    create_user(ADMIN_USER, ADMIN_PASS, role="admin")
    create_user(CLIENT_USER, CLIENT_PASS, role="client")


def test_login_success_admin_scope(client):
    """Admin user can obtain a token with 'admin' scope."""
    _ensure_users_created()
    response = client.post(
        "/auth/login",
        data={"username": ADMIN_USER, "password": ADMIN_PASS, "scope": "admin"},
    )
    assert response.status_code == 200, "Admin login did not return HTTP 200"
    data = response.json()
    assert "access_token" in data, "Missing 'access_token' in login response"
    assert data.get("token_type") == "bearer", "Token type is not 'bearer'"
    scopes = data.get("scopes", [])
    assert "admin" in scopes, "'admin' scope not granted to admin user"


def test_login_invalid_credentials(client):
    """Invalid password should return 401."""
    _ensure_users_created()
    response = client.post(
        "/auth/login",
        data={"username": ADMIN_USER, "password": "wrong", "scope": "admin"},
    )
    assert response.status_code == 401, "Invalid credentials did not yield 401"


def test_scopes_endpoint(client):
    """/auth/scopes returns available scopes mapping."""
    response = client.get("/auth/scopes")
    assert response.status_code == 200, "'/auth/scopes' did not return HTTP 200"
    data = response.json()
    assert "scopes" in data, "Missing 'scopes' key in scopes response"
    assert all(
        k in data["scopes"] for k in ["admin", "client"]
    ), "Expected scopes 'admin' and 'client' not present"
