from typing import Any

from app.amqp.abstract_amqp_message_factory import AbstractAMQPMessageFactory
from app.db.daos.reference_event_dao import ReferenceEventDAO
from app.db.models.reference_event import ReferenceEvent as DbReferenceEvent
from app.db.models.entity import Entity as DbEntity
from app.db.session import async_session
from app.models.entities import Entity as EntityModel
from app.models.reference_events import ReferenceEvent as ReferenceEventModel


class AMQPReferenceEventMessageFactory(AbstractAMQPMessageFactory):
    """Factory for building AMQP messages related to reference events."""

    def _build_routing_key(self) -> str:
        return "event.references.reference.event"

    async def _build_payload(self) -> dict[str, Any]:
        async with async_session() as session:
            async with session.begin():
                result = await ReferenceEventDAO(
                    session
                ).get_detailed_reference_event_by_id(self.content.get("id"))
                reference_event: DbReferenceEvent = result[0]
                entity: DbEntity = result[1]
                reference_event_representation: ReferenceEventModel = (
                    ReferenceEventModel.model_validate(reference_event)
                )
                return {
                    "reference_event": reference_event_representation.model_dump(
                        exclude={
                            "id": True,
                            "reference": {
                                "id": True,
                                "titles": {"__all__": {"id"}},
                                "subtitles": {"__all__": {"id"}},
                                "subjects": {
                                    "__all__": {
                                        "id": True,
                                        "labels": {"__all__": {"id"}},
                                    }
                                },
                            },
                        }
                    )
                } | {
                    "entity": EntityModel.model_validate(entity).model_dump(
                        exclude={"id": True}
                    )
                }
