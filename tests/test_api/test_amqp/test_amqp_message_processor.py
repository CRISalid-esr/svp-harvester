"""Test the references API."""
from unittest import mock

import pytest

from app.amqp.amqp_interface import AMQPInterface
from app.amqp.amqp_message_processor import AMQPMessageProcessor
from app.config import get_app_settings
from app.services.retrieval.retrieval_service import RetrievalService


@pytest.fixture
def mock_retrieval_service():
    """Retrieval service mock to detect run method calls."""
    with mock.patch.object(RetrievalService, "run", autospec=True) as service:
        yield service


@pytest.fixture()
async def message_processor() -> AMQPMessageProcessor:
    """AMQP message processor fixture to use AMQPInterface as factory."""
    amqp_connexion = AMQPInterface(get_app_settings())
    # pylint: disable=protected-access
    return await amqp_connexion._message_processor()


async def test_amqp_message(
    message_processor: AMQPMessageProcessor, mock_retrieval_service
):
    """Test that the retrieval service is called when a message is received."""
    payload = (
        b"{"
        b'"type": "person", '
        b'"fields": {'
        b'"first_name": "John", '
        b'"last_name": "Doe", '
        b'"identifiers": [{"type": "orcid", "value": "0000-0002-1825-0097"}]}'
        b"}"
    )
    # pylint: disable=protected-access
    await message_processor._process_message(payload.decode("utf-8"), 1)
    mock_retrieval_service.assert_called_once()
