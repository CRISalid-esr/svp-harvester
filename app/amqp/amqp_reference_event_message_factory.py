from typing import Any

from app.amqp.abstract_amqp_message_factory import AbstractAMQPMessageFactory
from app.db.daos import ReferenceEventDAO
from app.db.models.reference_event_model import ReferenceEvent
from app.db.session import async_session


class AMQPReferenceEventMessageFactory(AbstractAMQPMessageFactory):
    """Factory for building AMQP messages related to reference events."""

    def _build_routing_key(self) -> str:
        return "event.references.reference.event"

    async def _build_payload(self) -> dict[str, Any]:
        async with async_session() as session:
            async with session.begin():
                reference_event: ReferenceEvent = await ReferenceEventDAO(
                    session
                ).get_reference_event_by_id(self.content.get("id"))
                return {
                    "reference_event": reference_event.id,
                    "reference": reference_event.reference.id,
                    "title": reference_event.reference.titles[0].value,
                    "type": reference_event.type,
                }
