from typing import Any

from app.amqp.abstract_amqp_message_factory import AbstractAMQPMessageFactory
from app.db.daos.reference_event_dao import ReferenceEventDAO
from app.db.models.reference_event import ReferenceEvent as DbReferenceEvent
from app.db.session import async_session
from app.models.reference_events import ReferenceEvent as ReferenceEventModel


class AMQPReferenceEventMessageFactory(AbstractAMQPMessageFactory):
    """Factory for building AMQP messages related to reference events."""

    def _build_routing_key(self) -> str:
        return "event.references.reference.event"

    async def _build_payload(self) -> dict[str, Any]:
        async with async_session() as session:
            async with session.begin():
                reference_event: DbReferenceEvent = await ReferenceEventDAO(
                    session
                ).get_reference_event_by_id(self.content.get("id"))
                reference_event_representation: ReferenceEventModel = (
                    ReferenceEventModel.model_validate(reference_event)
                )
                return {"reference_event": reference_event_representation.model_dump()}
