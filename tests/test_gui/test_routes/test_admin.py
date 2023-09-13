"""Test the references API."""
from fastapi.testclient import TestClient


def test_admin_page(test_client: TestClient):
    """Test the create_retrieval_sync endpoint."""
    response = test_client.get("/admin")
    assert response.status_code == 200
