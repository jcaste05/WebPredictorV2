from backend.db.dev_init_db import create_user, init_db
from backend.tests.api.helpers import _auth_header

ADMIN_USER = "admin"
ADMIN_PASS = "adminpass"
CLIENT_USER = "client"
CLIENT_PASS = "clientpass"


def _ensure_users_and_get_client_token(client):
    init_db()
    create_user(ADMIN_USER, ADMIN_PASS, role="admin")
    create_user(CLIENT_USER, CLIENT_PASS, role="client")
    # login client requesting client scope
    resp = client.post(
        "/auth/login",
        data={"username": CLIENT_USER, "password": CLIENT_PASS, "scope": "client"},
    )
    assert resp.status_code == 200, "Client login did not return HTTP 200"
    return resp.json()["access_token"]


def test_available_models_endpoint(client):
    """/tabular_regressor/available_models returns expected list."""
    token = _ensure_users_and_get_client_token(client)
    resp = client.post(
        "/tabular_regressor/available_models", headers=_auth_header(token)
    )
    assert resp.status_code == 200, "'available_models' did not return HTTP 200"
    data = resp.json()
    assert "available_models" in data, "Missing 'available_models' key"
    assert isinstance(
        data["available_models"], list
    ), "'available_models' is not a list"
    assert len(data["available_models"]) > 0, "'available_models' list is empty"


def test_train_predict_endpoint(client):
    """Minimal training + prediction flow returns metrics and predictions."""
    token = _ensure_users_and_get_client_token(client)
    train_rows = [
        {"index": 1, "feat1": 0.1, "target1": 10.0},
        {"index": 2, "feat1": 0.2, "target1": 20.0},
        {"index": 3, "feat1": 0.3, "target1": 30.0},
    ]
    predict_rows = [
        {"index": 101, "feat1": 0.15},
        {"index": 102, "feat1": 0.25},
    ]
    payload = {
        "model_type": "LinearRegression",
        "target_columns": ["target1"],
        "feature_columns": ["feat1"],
        "train_data": {"rows": train_rows},
        "predict_data": {"rows": predict_rows},
    }
    resp = client.post(
        "/tabular_regressor/train_predict", json=payload, headers=_auth_header(token)
    )
    assert resp.status_code == 200, "'train_predict' did not return HTTP 200"
    data = resp.json()
    expected_keys = {
        "model_type",
        "model_version",
        "api_version",
        "targets",
        "metrics",
        "predictions",
    }
    # Check keys
    missing = expected_keys - set(data.keys())
    assert not missing, f"TrainPredict response missing keys: {missing}"
    # Check contents
    assert data["model_type"] == "LinearRegression", "Model type mismatch"
    assert data["targets"] == ["target1"], "Targets list mismatch"
    preds = data["predictions"]
    assert len(preds) == 2, "Predictions length mismatch"
    for p in preds:
        assert "index" in p, "Prediction missing 'index'"
        assert "values" in p, "Prediction missing 'values'"
        assert "target1_hat" in p["values"], "Prediction missing 'target1_hat' key"
        assert isinstance(
            p["values"]["target1_hat"], (int, float)
        ), "Predicted value is not numeric"
