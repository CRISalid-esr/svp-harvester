from typing import AsyncGenerator

from semver import VersionInfo, Version

from app.db.models.contributor_identifier import ContributorIdentifier
from app.harvesters.abstract_harvester import AbstractHarvester
from app.harvesters.scopus.scopus_api_query_builder import ScopusQueryBuilder
from app.harvesters.scopus.scopus_client import ScopusClient
from app.harvesters.xml_harvester_raw_result import XMLHarvesterRawResult


class ScopusHarvester(AbstractHarvester):
    """
    Harvester for Scopus
    """

    FORMATTER_NAME = "scopus"

    IDENTIFIERS_BY_ENTITIES = {
        "Person": [
            (
                ContributorIdentifier.IdentifierType.SCOPUS.value,
                ScopusQueryBuilder.QueryParameters.SCOPUS_EID,
            )
        ]
    }

    SUBJECT_BY_ENTITIES = {"Person": ScopusQueryBuilder.SubjectType.PERSON}

    VERSION: Version = VersionInfo.parse("2.1.0")

    async def _get_scopus_query_parameters(self, entity_class: str):
        """
        Return the Scopus query parameters using the pre-selected entity identifier.
        """
        assert self.entity_identifier_used is not None, (
            "entity_identifier_used must be set before calling _get_scopus_query_parameters"
        )
        identifier_key, identifier_value = self.entity_identifier_used
        for entry_key, scopus_query_parameter in self.IDENTIFIERS_BY_ENTITIES.get(
            entity_class, []
        ):
            if entry_key == identifier_key:
                return scopus_query_parameter, identifier_value
        assert False, f"Unable to map '{identifier_key}' to Scopus query parameter"

    async def fetch_results(self) -> AsyncGenerator[XMLHarvesterRawResult, None]:
        """
        Fetch results from the Scopus API
        """
        builder = ScopusQueryBuilder()

        identifier_type, identifier_value = await self._get_scopus_query_parameters(
            await self._get_entity_class_name()
        )

        builder.set_subject_type(
            self.SUBJECT_BY_ENTITIES[await self._get_entity_class_name()]
        )

        builder.set_query(identifier_type, identifier_value)
        async for doc in ScopusClient().fetch(builder.build()):
            if doc is None:
                continue
            source_identifier = doc.find(
                "dc:identifier", ScopusClient.NAMESPACE
            ).text.split(":")[-1]
            yield XMLHarvesterRawResult(
                payload=doc,
                source_identifier=source_identifier,
                formatter_name=ScopusHarvester.FORMATTER_NAME,
            )
