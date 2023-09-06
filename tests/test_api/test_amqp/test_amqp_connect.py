"""Test the references API."""
from unittest import mock

import aio_pika
import aiormq
import pytest
from amqp_mock import create_amqp_mock, Message

from app.api.amqp.amqp_connect import AMQPConnexion
from app.config import get_app_settings
from app.services.harvester.retrieval_service import RetrievalService


@pytest.fixture
def mock_retrieval_service():
    with mock.patch.object(
        RetrievalService, "retrieve", autospec=True
    ) as mock_retrieval_service:
        yield mock_retrieval_service


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
    amqp_connexion = AMQPConnexion(get_app_settings())
    await amqp_connexion._process_message_payload(payload)
    mock_retrieval_service.assert_called_once()
