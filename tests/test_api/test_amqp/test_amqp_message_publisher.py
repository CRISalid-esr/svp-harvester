"""Test AMQP publishing capabilities."""
from unittest import mock
from unittest.mock import Mock, AsyncMock

import aio_pika
import pytest
from aio_pika import Exchange, Channel, Connection, DeliveryMode
from yarl import URL

from app.amqp.amqp_message_publisher import AMQPMessagePublisher


@pytest.fixture(name="mocked_message")
def mock_message():
    """Retrieval service mock to detect run method calls."""
    with mock.patch.object(aio_pika, "Message") as exch:
        yield exch


async def test_publish_harvesting_status(mocked_message: Mock, harvesting_db_model):
    """Test that a message is published to the AMQP queue when the publish method is called."""
    mock_exchange = Exchange(
        Channel(Connection(URL("http://foobar"))), "tests_amqp_queue"
    )
    mock_exchange.publish = AsyncMock()
    amqp_message_publisher = AMQPMessagePublisher(mock_exchange)
    received_message_payload = {"type": "Harvesting", "id": harvesting_db_model.id}
    expected_sent_message_payload = {
        "harvesting": 1,
        "harvester": "idref",
        "state": "running",
        "retrieval": 1,
    }
    expected_sent_message_routing_key = "event.references.harvesting.state"
    await amqp_message_publisher.publish(received_message_payload)
    mocked_message.assert_called_once_with(
        str(expected_sent_message_payload).encode(),
        delivery_mode=DeliveryMode.PERSISTENT,
    )
    mock_exchange.publish.assert_called_once_with(
        message=mocked_message.return_value,
        routing_key=expected_sent_message_routing_key,
    )
