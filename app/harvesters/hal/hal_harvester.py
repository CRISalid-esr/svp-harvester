from typing import AsyncGenerator

from app.db.models import Entity
from app.harvesters.abstract_harvester import AbstractHarvester
from app.harvesters.hal.hal_api_client import HalApiClient
from app.harvesters.hal.hal_api_query_builder import HalApiQueryBuilder
from app.harvesters.json_harvester_raw_result import (
    JsonHarvesterRawResult as JsonRawResult,
)


class HalHarvester(AbstractHarvester):
    """
    Harvester for data.idref.fl
    """

    FORMATTER_NAME = "HAL"

    async def fetch_results(self) -> AsyncGenerator[JsonRawResult, None]:
        builder = HalApiQueryBuilder()
        if (await self._get_entity_class_name()) == "Person":
            id_hal_i: str = (await self._get_entity()).get_identifier("id_hal_i")
            assert (
                id_hal_i is not None
            ), "Unable to run hal harvester for a person without id_hal"
            builder.set_query(
                identifier_type=HalApiQueryBuilder.QueryParameters.AUTH_ID_HAL_I,
                identifier_value=id_hal_i,
            )
        async for doc in HalApiClient().fetch(builder.build()):
            yield JsonRawResult(
                payload=doc,
                source_identifier=doc.get("docid"),
                formatter_name=HalHarvester.FORMATTER_NAME,
            )

    def is_relevant(self, entity: Entity) -> bool:
        return entity.get_identifier("id_hal_i") is not None
