from typing import Any

from app.api.amqp.abstract_amqp_message_factory import AbstractAMQPMessageFactory
from app.db.daos import HarvestingDAO
from app.db.session import async_session


class AMQPHarvestingMessageFactory(AbstractAMQPMessageFactory):
    """Factory for building AMQP messages related to harvesting states."""

    def _build_routing_key(self) -> str:
        return "event.references.harvesting.state"

    async def _build_payload(self) -> dict[str, Any]:
        async with async_session() as session:
            async with session.begin():
                harvesting = await HarvestingDAO(session).get_harvesting_by_id(
                    self.content["id"]
                )
                return {
                    "harvesting": harvesting.id,
                    "harvester": harvesting.harvester,
                    "state": harvesting.state,
                    "retrieval": harvesting.retrieval_id,
                }
