def test_health_endpoint(client):
    """Test that the health endpoint returns OK."""
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"

def test_docs_and_redoc_endpoints(client):
    """Test that the /docs and /redoc endpoints are accessible."""
    response_docs = client.get("/docs")
    response_redoc = client.get("/redoc")
    
    assert response_docs.status_code == 200
    assert response_redoc.status_code == 200
