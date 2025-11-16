from backend.db.dev_init_db import create_user, init_db
from backend.tests.api.helpers import _auth_header

ADMIN_USER = "admin"
ADMIN_PASS = "adminpass"
TEST_USER = "tempuser"
TEST_PASS = "temppass"


def _bootstrap_admin_and_test_user(client):
    init_db()
    create_user(ADMIN_USER, ADMIN_PASS, role="admin")
    create_user(TEST_USER, TEST_PASS, role="client")
    resp = client.post(
        "/auth/login",
        data={"username": ADMIN_USER, "password": ADMIN_PASS, "scope": "admin"},
    )
    assert resp.status_code == 200, "Admin login failed during bootstrap"
    return resp.json()["access_token"]


def test_list_users(client):
    """Admin can list users."""
    token = _bootstrap_admin_and_test_user(client)
    resp = client.get("/admin/", headers=_auth_header(token))
    assert resp.status_code == 200, "Listing users did not return HTTP 200"
    data = resp.json()
    assert isinstance(data, list), "List users response is not a list"
    assert any(u["user"] == ADMIN_USER for u in data), "Admin user missing from list"


def test_create_user_conflict(client):
    """Creating an existing user should return 409."""
    token = _bootstrap_admin_and_test_user(client)
    payload = {"user": TEST_USER, "password": TEST_PASS, "role": "client"}
    resp = client.post("/admin/create_user", json=payload, headers=_auth_header(token))
    assert resp.status_code in (200, 409), "Unexpected status creating temp user"
    resp2 = client.post("/admin/create_user", json=payload, headers=_auth_header(token))
    assert resp2.status_code == 409, "Duplicate user creation did not return 409"


def test_get_user_by_username(client):
    """Admin retrieves user by username."""
    token = _bootstrap_admin_and_test_user(client)
    payload = {"user": TEST_USER}
    resp = client.post("/admin/get_user", json=payload, headers=_auth_header(token))
    assert resp.status_code == 200, "Get user by username did not return HTTP 200"
    data = resp.json()
    assert (
        data.get("user") == TEST_USER
    ), "Returned user does not match requested username"


def test_change_password_and_role(client):
    """Admin changes user password and role."""
    token = _bootstrap_admin_and_test_user(client)
    new_pass = "newpass"
    payload = {"user": TEST_USER, "password": new_pass, "role": "client"}
    resp = client.post(
        "/admin/change_password", json=payload, headers=_auth_header(token)
    )
    assert resp.status_code == 200, "Change password endpoint did not return HTTP 200"
    data = resp.json()
    assert data.get("user") == TEST_USER, "Changed user mismatch"
    assert data.get("role") == "client", "Role not updated as expected"


def test_delete_user(client):
    """Admin deletes a user by username."""
    token = _bootstrap_admin_and_test_user(client)
    payload = {"user": TEST_USER}
    resp = client.post("/admin/delete_user", json=payload, headers=_auth_header(token))
    assert resp.status_code == 200, "Delete user did not return HTTP 200"
    data = resp.json()
    assert data.get("user") == TEST_USER, "Deleted user mismatch"

    resp2 = client.post("/admin/get_user", json=payload, headers=_auth_header(token))
    assert resp2.status_code == 404, "Deleted user retrieval did not return 404"
