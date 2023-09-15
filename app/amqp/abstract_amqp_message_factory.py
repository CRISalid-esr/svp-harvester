from abc import ABC, abstractmethod


class AbstractAMQPMessageFactory(ABC):
    """Abstract factory for building AMQP messages."""

    def __init__(self, content):
        self.content = content

    async def build_message(self) -> tuple[str, str]:
        """Build the message routing key and payload."""
        return self._build_routing_key(), await self._build_payload()

    @abstractmethod
    def _build_routing_key(self) -> str:
        raise NotImplementedError()

    @abstractmethod
    async def _build_payload(self) -> str:
        raise NotImplementedError()
