"""Test the references API."""
from unittest import mock

import pytest

from app.api.amqp.amqp_interface import AMQPInterface
from app.config import get_app_settings
from app.services.retrieval.retrieval_service import RetrievalService


@pytest.fixture
def mock_retrieval_service():
    with mock.patch.object(
        RetrievalService, "run", autospec=True
    ) as mock_retrieval_service:
        yield mock_retrieval_service


# @pytest.mark.skip(reason="Process is stuck on asyncio.gather")
@pytest.mark.asyncio
async def test_amqp_message(mock_retrieval_service):
    payload = (
        b"{"
        b'"type": "person", '
        b'"fields": {'
        b'"first_name": "John", '
        b'"last_name": "Doe", '
        b'"identifiers": [{"type": "orcid", "value": "0000-0002-1825-0097"}]}'
        b"}"
    )
    amqp_connexion = AMQPInterface(get_app_settings())
    await amqp_connexion._process_message_payload(payload.decode("utf-8"), 1)
    mock_retrieval_service.assert_called_once()
