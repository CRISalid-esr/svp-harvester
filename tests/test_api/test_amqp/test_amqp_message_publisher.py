"""Test AMQP publishing capabilities."""
from unittest import mock
from unittest.mock import Mock, AsyncMock

import aio_pika
import pytest
from aio_pika import Exchange, Channel, Connection, DeliveryMode
from sqlalchemy.ext.asyncio import AsyncSession
from yarl import URL

from app.amqp.amqp_message_publisher import AMQPMessagePublisher


@pytest.fixture(name="mocked_message")
def mock_message():
    """Retrieval service mock to detect run method calls."""
    with mock.patch.object(aio_pika, "Message") as exch:
        yield exch


@pytest.fixture(name="mocked_exchange")
def mock_exchange():
    """
    Mocked RabbitMQ exchange to control publish calls.
    """
    mocked_exchange = Exchange(
        Channel(Connection(URL("http://foobar"))), "tests_amqp_queue"
    )
    mocked_exchange.publish = AsyncMock()
    return mocked_exchange


@pytest.mark.asyncio
async def test_publish_harvesting_status(
    async_session: AsyncSession,
    mocked_message: Mock,
    mocked_exchange: Exchange,
    harvesting_db_model,
):
    """Test that a message is published to the AMQP queue when the publish method is called."""
    async_session.add(harvesting_db_model)
    await async_session.commit()

    amqp_message_publisher = AMQPMessagePublisher(mocked_exchange)
    received_message_payload = {"type": "Harvesting", "id": harvesting_db_model.id}
    expected_sent_message_payload = {
        "harvester": "idref",
        "state": "running",
        "entity": {
            "identifiers": [{"type": "idref", "value": "123456789"}],
            "name": "John Doe",
        },
    }
    expected_sent_message_routing_key = "event.references.harvesting.state"
    await amqp_message_publisher.publish(received_message_payload)
    mocked_message.assert_called_once_with(
        str(expected_sent_message_payload).encode(),
        delivery_mode=DeliveryMode.PERSISTENT,
    )
    mocked_exchange.publish.assert_called_once_with(
        message=mocked_message.return_value,
        routing_key=expected_sent_message_routing_key,
    )


@pytest.mark.current
@pytest.mark.asyncio
async def test_publish_created_reference(
    async_session: AsyncSession,
    mocked_message: Mock,
    mocked_exchange: Exchange,
    reference_event_db_model,
):
    """Test that a message is published to the AMQP queue when the publish method is called."""
    async_session.add(reference_event_db_model)
    await async_session.commit()

    amqp_message_publisher = AMQPMessagePublisher(mocked_exchange)
    received_message_payload = {
        "type": "ReferenceEvent",
        "id": reference_event_db_model.id,
        "state": "created",
    }
    expected_sent_message_payload = {
        "reference_event": {
            "type": "created",
            "reference": {
                "source_identifier": "123456789",
                "titles": [{"value": "title", "language": "fr"}],
                "subtitles": [{"value": "subtitle", "language": "fr"}],
                "subjects": [
                    {
                        "uri": "http://uri",
                        "labels": [{"value": "label", "language": "fr"}],
                    }
                ],
            },
        },
        "entity": {
            "identifiers": [{"type": "idref", "value": "123456789"}],
            "name": "John Doe",
        },
    }

    expected_sent_message_routing_key = "event.references.reference.event"
    await amqp_message_publisher.publish(received_message_payload)
    mocked_message.assert_called_once_with(
        str(expected_sent_message_payload).encode(),
        delivery_mode=DeliveryMode.PERSISTENT,
    )
    mocked_exchange.publish.assert_called_once_with(
        message=mocked_message.return_value,
        routing_key=expected_sent_message_routing_key,
    )
