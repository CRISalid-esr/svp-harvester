"""Test the references API."""
import logging

import pytest
from _pytest.logging import LogCaptureFixture
from fastapi.testclient import TestClient


@pytest.mark.skip(reason="Middleware has been disabled")
def test_request_with_unprocessable_entity_logged(
    test_client: TestClient, caplog: LogCaptureFixture
):
    """
    Test validation error when calling create_retrieval_sync endpoint with name only.
    :param test_client:
    :return:
    """
    caplog.set_level(logging.INFO)
    test_client.get("/api/v1/references?name=Bourdieu")
    messages = [record.message for record in caplog.records]
    assert "Request to access /api/v1/references" in messages
    assert any("HTTP/1.1 422 Unprocessable Entity" in m for m in messages) is True


@pytest.mark.skip(reason="Middleware has been disabled")
def test_valid_request_logged(
    test_client: TestClient,
    person_with_name_and_idref_json,
    caplog: LogCaptureFixture,
):
    """Test the create_retrieval_sync endpoint."""
    caplog.set_level(logging.INFO)
    test_client.post(
        "/api/v1/references/retrieval",
        json=person_with_name_and_idref_json,
    )
    messages = [record.message for record in caplog.records]
    assert "Request to access /api/v1/references/retrieval" in messages
    assert "Successfully accessed /api/v1/references/retrieval" in messages
