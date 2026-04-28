from typing import AsyncGenerator

from semver import VersionInfo, Version

from app.db.models.contributor_identifier import ContributorIdentifier
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

    FORMATTER_NAME = "hal"

    IDENTIFIERS_BY_ENTITIES = {
        "Person": [
            (
                ContributorIdentifier.IdentifierType.IDHAL_I.value,
                HalApiQueryBuilder.QueryParameters.AUTH_ID_HAL_I,
            ),
            (
                ContributorIdentifier.IdentifierType.IDHAL_S.value,
                HalApiQueryBuilder.QueryParameters.AUTH_ID_HAL_S,
            ),
            (
                ContributorIdentifier.IdentifierType.ORCID.value,
                HalApiQueryBuilder.QueryParameters.AUTH_ORCID_ID_EXT_ID,
            ),
        ]
    }

    VERSION: Version = VersionInfo.parse("2.1.1")

    async def _get_hal_query_parameters(self, entity_class: str):
        """
        Return the HAL query parameters using the pre-selected entity identifier.
        """
        assert self.entity_identifier_used is not None, (
            "entity_identifier_used must be set before calling _get_hal_query_parameters"
        )
        identifier_key, identifier_value = self.entity_identifier_used
        for entry_key, hal_query_parameter in self.IDENTIFIERS_BY_ENTITIES.get(
            entity_class, []
        ):
            if entry_key == identifier_key:
                return hal_query_parameter, identifier_value
        assert False, f"Unable to map '{identifier_key}' to HAL query parameter"

    async def fetch_results(self) -> AsyncGenerator[JsonRawResult, None]:
        """
        Fetch results from the HAL API.
        It is an asynchronous generator that yields JsonRawResult objects.
        """
        builder = HalApiQueryBuilder()

        identifier_type, identifier_value = await self._get_hal_query_parameters(
            await self._get_entity_class_name()
        )

        builder.set_query(
            identifier_type=identifier_type,
            identifier_value=identifier_value,
        )
        async for doc in HalApiClient().fetch(builder.build()):
            yield JsonRawResult(
                payload=doc,
                source_identifier=doc.get("halId_s"),
                formatter_name=HalHarvester.FORMATTER_NAME,
            )
