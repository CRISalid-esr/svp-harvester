"""Test the references API."""
from fastapi import FastAPI
from fastapi.testclient import TestClient

app = FastAPI()

client = TestClient(app)


def test_fetch_references_sync_for_person_with_idref():
    """Test the fetch_references_for_person_sync endpoint."""
    response = client.get("references?idref=123456789")
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello World"}
