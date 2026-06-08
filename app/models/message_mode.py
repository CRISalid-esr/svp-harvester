from enum import StrEnum


class MessageMode(StrEnum):
    """Routing mode segment appended to every AMQP routing key (5th segment)."""

    BATCH = "batch"
    INTERACTIVE = "interactive"
