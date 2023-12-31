from typing import AsyncGenerator, Type

from app.db.models.entity import Entity as DbEntity
from app.harvesters.abstract_harvester import AbstractHarvester
from app.harvesters.json_harvester_raw_result import JsonHarvesterRawResult as RawResult

from app.harvesters.scanr.scanr_api_query_builder import ScanRApiQueryBuilder as QueryBuilder
from app.harvesters.scanr.scanr_elastic_client import ScanRElasticClient


class ScanrHarvester(AbstractHarvester):
    """
    Harvester for Scanr API
    """
    FORMATTER_NAME = "SCANR"

    IDENTIFIERS_BY_ENTITIES = {
        "Person": [
            (QueryBuilder.QueryParameters.AUTH_IDREF, "idref"),
            (QueryBuilder.QueryParameters.AUTH_ORCID, "orcid"),
            (QueryBuilder.QueryParameters.AUTH_ID_HAL_S, "id_hal"),
        ]
    }

    async def _get_scanr_query_parameters(self, entity_class: str):
        """
        Set the query parameters for an entity
        """
        entity = await self._get_entity()

        query_parameters = self.IDENTIFIERS_BY_ENTITIES.get(entity_class)
        # List convenient query parameters for this entity class
        # and choose the first one for which value is provided

        for scanr_query_parameter, identifier_key in query_parameters:
            identifier_value = entity.get_identifier(identifier_key)
            if identifier_value is not None:
                return scanr_query_parameter, str(identifier_value)

        assert (
            False
        ), "Unable to run hal harvester for a person without idref"

    async def fetch_results(self) -> AsyncGenerator[RawResult, None]:

        async with ScanRElasticClient() as client:

            builder = QueryBuilder()

            identifier_type, identifier_value = await self._get_scanr_query_parameters(
                await self._get_entity_class_name()
            )

            if identifier_type != QueryBuilder.QueryParameters.AUTH_IDREF:
                # If we want the publications tied to an entity,
                # but we don't know the main id used by scanr,
                # we need to get it first by doing a search in the corresponding indice.
                print("Condition met, doing something...")

            builder.set_subject_type(builder.SubjectType.PUBLICATION)

            builder.set_query(
                identifier_type=identifier_type,
                identifier_value=identifier_value
            )

            client.set_query(elastic_query=builder.build())
            async for doc in client.perform_search(client.Indexes.PUBLICATIONS):
                yield RawResult(
                    payload=doc,
                    source_identifier=doc.get("_id"),
                    formatter_name=ScanrHarvester.FORMATTER_NAME,
                )

    def is_relevant(self, entity: Type[DbEntity]) -> bool:
        """Check if one of the given identifiers is relevant for the harvester"""
        identifier_types = ["idref"]

        return any(
            entity.get_identifier(identifier_type=identifier_type) is not None
            for identifier_type in identifier_types
        )
