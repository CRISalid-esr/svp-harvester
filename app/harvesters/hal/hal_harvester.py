from app.db.models import Identifier, Entity
from app.harvesters.abstract_harvester import AbstractHarvester
from app.harvesters.hal.hal_api_client import HalApiClient
from app.harvesters.hal.hal_api_query_builder import HalApiQueryBuilder
from app.models.identifiers import IdentifierTypeEnum


class HalHarvester(AbstractHarvester):
    """
    Harvester for data.idref.fl
    """

    async def fetch_results(self):
        builder = HalApiQueryBuilder()
        if (await self._get_entity()).__class__.__name__ == "Person":
            id_hal_i: str = (await self._get_entity()).get_identifier(
                Identifier.Type.ID_HAL_I
            )
            assert (
                id_hal_i is not None
            ), "Unable to run hal harvester for a person without id_hal"
            builder.set_query(
                identifier_type=HalApiQueryBuilder.QueryParameters.AUTH_ID_HAL_I,
                identifier_value=id_hal_i,
            )
        async for doc in HalApiClient().fetch(builder.build()):
            yield doc

    def is_relevant(self, entity: Entity) -> bool:
        return entity.get_identifier(IdentifierTypeEnum.ID_HAL_I) is not None
