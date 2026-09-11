from typing import AsyncGenerator

from semver import VersionInfo, Version

from app.db.models.contributor_identifier import ContributorIdentifier
from app.harvesters.abstract_harvester import AbstractHarvester
from app.harvesters.json_harvester_raw_result import JsonHarvesterRawResult as RawResult
from app.harvesters.scanr.scanr_api_query_builder import (
    ScanRApiQueryBuilder as QueryBuilder,
)
from app.harvesters.scanr.scanr_elastic_client import ScanRElasticClient


class ScanrHarvester(AbstractHarvester):
    """
    Harvester for Scanr API
    """

    FORMATTER_NAME = "scanr"

    IDENTIFIERS_BY_ENTITIES = {
        "Person": [
            (
                ContributorIdentifier.IdentifierType.IDREF.value,
                QueryBuilder.QueryParameters.AUTH_IDREF,
            ),
            (
                ContributorIdentifier.IdentifierType.ORCID.value,
                QueryBuilder.QueryParameters.AUTH_ORCID,
            ),
            (
                ContributorIdentifier.IdentifierType.IDHAL_S.value,
                QueryBuilder.QueryParameters.AUTH_ID_HAL_S,
            ),
        ]
    }

    VERSION: Version = VersionInfo.parse("2.2.0")

    async def _get_scanr_query_parameters(self, entity_class: str):
        """
        Compute the ScanR person id using the pre-selected entity identifier.
        Returns a scanr_id string, or None if not found.
        """
        assert (
            self.entity_identifier_used is not None
        ), "entity_identifier_used must be set before calling _get_scanr_query_parameters"
        identifier_key, identifier_value = self.entity_identifier_used
        for entry_key, scanr_query_parameter in self.IDENTIFIERS_BY_ENTITIES.get(
            entity_class, []
        ):
            if entry_key != identifier_key:
                continue
            if identifier_key == "idref":
                return identifier_key + str(identifier_value)
            return await self._get_entity_scanr_id(
                scanr_query_parameter, identifier_value
            )
        return None

    async def fetch_results(self) -> AsyncGenerator[RawResult, None]:
        async with ScanRElasticClient() as client:
            builder = QueryBuilder()

            scanr_id = await self._get_scanr_query_parameters(
                await self._get_entity_class_name()
            )
            if scanr_id is None:
                return
            builder.set_publication_query(scanr_id=scanr_id)

            client.set_query(elastic_query=builder.build())
            async for doc in client.perform_search(client.Indexes.PUBLICATIONS):
                yield RawResult(
                    payload=doc,
                    source_identifier=doc["_source"].get("id"),
                    formatter_name=ScanrHarvester.FORMATTER_NAME,
                )

    @staticmethod
    async def _get_entity_scanr_id(identifier_type, identifier_value: str):
        async with ScanRElasticClient() as client:
            builder = QueryBuilder()
            builder.set_person_query(identifier_type, identifier_value)

            client.set_query(elastic_query=builder.build())
            async for doc in client.perform_search(client.Indexes.PERSONS):
                return doc.get("_source", {}).get("id")
