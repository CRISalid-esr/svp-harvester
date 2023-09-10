"""Test the references API."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession


def test_fetch_references_sync_with_idref(
    test_client: TestClient, async_session: AsyncSession
):
    """Test the create_retrieval_sync endpoint."""
    response = test_client.get("/api/v1/references?idref=123456789")
    assert response.status_code == 200


def test_fetch_references_async_with_name_and_idref(
    test_client: TestClient,
    async_session: AsyncSession,
    person_with_name_and_idref_json,
):
    """Test the create_retrieval_sync endpoint."""
    response = test_client.post(
        "/api/v1/references/retrieval",
        json=person_with_name_and_idref_json,
    )
    assert response.status_code == 200
