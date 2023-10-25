from unittest import mock
from unittest.mock import AsyncMock

import aio_pika
import pytest
from aio_pika import Exchange, Channel, Connection
from yarl import URL


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
