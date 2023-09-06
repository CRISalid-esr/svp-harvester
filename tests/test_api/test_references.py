"""Test the references API."""
from fastapi.testclient import TestClient


def test_fetch_references_sync_for_person_with_idref(test_client: TestClient):
    """Test the fetch_references_for_person_sync endpoint."""
    response = test_client.get("/api/v1/references?idref=123456789")
    assert response.status_code == 200


def test_fetch_references_sync_for_person_with_idref2(test_client: TestClient):
    """Test the fetch_references_for_person_sync endpoint."""
    response = test_client.get("/api/v1/references?idref=toto")
    assert response.status_code == 200
