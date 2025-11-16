def test_health_endpoint(client):
    """Ensure /health returns expected structure and status."""
    response = client.get("/health")
    assert response.status_code == 200, "'/health' did not return HTTP 200"
    data = response.json()
    assert data.get("status") == "ok", "Health status is not 'ok'"
    required_keys = {
        "service_name",
        "description",
        "api_version",
        "model_version",
        "resources",
        "links",
    }
    missing = required_keys - set(data.keys())
    assert not missing, f"'/health' response missing keys: {missing}"


def test_docs_and_redoc_endpoints(client):
    """Verify that /docs and /redoc are accessible and return HTML."""
    response_docs = client.get("/docs")
    response_redoc = client.get("/redoc")
    assert response_docs.status_code == 200, "'/docs' did not return HTTP 200"
    assert response_redoc.status_code == 200, "'/redoc' did not return HTTP 200"
    assert "text/html" in response_docs.headers.get(
        "content-type", ""
    ), "'/docs' did not return HTML content"
    assert "text/html" in response_redoc.headers.get(
        "content-type", ""
    ), "'/redoc' did not return HTML content"


def test_openapi_schema_available(client):
    """Ensure the OpenAPI schema is available at /openapi.json."""
    resp = client.get("/openapi.json")
    assert resp.status_code == 200, "'/openapi.json' did not return HTTP 200"
    schema = resp.json()
    assert "openapi" in schema, "OpenAPI schema missing 'openapi' key"
    assert "paths" in schema, "OpenAPI schema missing 'paths' key"


def test_root_serves_frontend_index(client):
    """Ensure root '/' serves the frontend index file."""
    resp = client.get("/")
    assert resp.status_code == 200, "Root '/' did not return HTTP 200"
    ct = resp.headers.get("content-type", "")
    assert "text/html" in ct, "Root '/' did not return HTML content"


def test_favicon_endpoint(client):
    """Ensure /favicon.ico returns an image file."""
    resp = client.get("/favicon.ico")
    assert resp.status_code == 200, "'/favicon.ico' did not return HTTP 200"
    ct = resp.headers.get("content-type", "")
    assert any(
        img in ct for img in ["image/png", "image/x-icon", "application/octet-stream"]
    ), "Favicon content-type unexpected"
