from typing import Any

from app.amqp.abstract_amqp_message_factory import AbstractAMQPMessageFactory
from app.db.daos.harvesting_dao import HarvestingDAO
from app.db.models.harvesting import Harvesting as DbHarvesting
from app.db.session import async_session
from app.models.harvesting import Harvesting as HarvestingModel
from app.models.entities import Entity as EntityModel


class AMQPHarvestingMessageFactory(AbstractAMQPMessageFactory):
    """Factory for building AMQP messages related to harvesting states."""

    def _build_routing_key(self) -> str:
        return self.settings.amqp_harvesting_event_routing_key

    async def _build_payload(self) -> dict[str, Any]:
        assert "id" in self.content, "Harvesting id is required"
        async with async_session() as session:
            harvesting: DbHarvesting = await HarvestingDAO(
                session
            ).get_harvesting_extended_info_by_id(self.content.get("id"))
            harvesting_representation: HarvestingModel = HarvestingModel.model_validate(
                harvesting
            )
            entity_representation: EntityModel = EntityModel.model_validate(
                harvesting.retrieval.entity
            )
        return harvesting_representation.model_dump(
            exclude={"id": True, "reference_events": True}
        ) | {"entity": entity_representation.model_dump(exclude={"id": True})}
