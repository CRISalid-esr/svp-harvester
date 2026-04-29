from typing import AsyncGenerator

from semver import VersionInfo, Version

from app.db.models.contributor_identifier import ContributorIdentifier
from app.harvesters.abstract_harvester import AbstractHarvester
from app.harvesters.json_harvester_raw_result import JsonHarvesterRawResult
from app.harvesters.open_alex.open_alex_api_query_builder import OpenAlexQueryBuilder
from app.harvesters.open_alex.open_alex_client import OpenAlexClient


class OpenAlexHarvester(AbstractHarvester):
    """
    Harvester for api.openalex.org
    """

    FORMATTER_NAME = "openalex"

    IDENTIFIERS_BY_ENTITIES = {
        "Person": [
            (
                ContributorIdentifier.IdentifierType.ORCID.value,
                OpenAlexQueryBuilder.QueryParameters.AUTH_ORCID,
            )
        ]
    }

    SUBJECT_BY_ENTITIES = {"Person": OpenAlexQueryBuilder.SubjectType.PERSON}

    VERSION: Version = VersionInfo.parse("2.2.0")

    async def _get_open_alex_query_parameters(self, entity_class: str):
        """
        Return the OpenAlex query parameters using the pre-selected entity identifier.
        """
        assert (
            self.entity_identifier_used is not None
        ), "entity_identifier_used must be set before calling _get_open_alex_query_parameters"
        identifier_key, identifier_value = self.entity_identifier_used
        for entry_key, open_alex_query_parameter in self.IDENTIFIERS_BY_ENTITIES.get(
            entity_class, []
        ):
            if entry_key == identifier_key:
                return open_alex_query_parameter, identifier_value
        assert False, f"Unable to map '{identifier_key}' to OpenAlex query parameter"

    async def fetch_results(self) -> AsyncGenerator[JsonHarvesterRawResult, None]:
        """
        Fetch results from the OpenAlex API.
        It is an asynchronous generator that yields JsonHarvesterRawResult objects.
        """
        builder = OpenAlexQueryBuilder()

        identifier_type, identifier_value = await self._get_open_alex_query_parameters(
            await self._get_entity_class_name()
        )

        builder.set_subject_type(
            self.SUBJECT_BY_ENTITIES[await self._get_entity_class_name()]
        )

        builder.set_query(
            identifier_type=identifier_type, identifier_value=identifier_value
        )

        async for doc in OpenAlexClient().fetch(builder.build()):
            yield JsonHarvesterRawResult(
                payload=doc,
                source_identifier=doc.get("id"),
                formatter_name=OpenAlexHarvester.FORMATTER_NAME,
            )
