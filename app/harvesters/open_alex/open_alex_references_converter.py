from typing import AsyncGenerator

import isodate
from loguru import logger
from semver import Version

from app.db.models.abstract import Abstract
from app.db.models.concept import Concept
from app.db.models.contribution import Contribution
from app.db.models.issue import Issue
from app.db.models.journal import Journal
from app.db.models.reference import Reference
from app.db.models.title import Title
from app.db.models.reference_identifier import ReferenceIdentifier
from app.harvesters.abstract_references_converter import AbstractReferencesConverter
from app.harvesters.json_harvester_raw_result import (
    JsonHarvesterRawResult as JsonRawResult,
)
from app.harvesters.open_alex.open_alex_document_type_converter import (
    OpenAlexDocumentTypeConverter,
)
from app.services.concepts.concept_informations import ConceptInformations
from app.services.hash.hash_key import HashKey
from app.services.issue.issue_data_class import IssueInformations
from app.services.journal.journal_data_class import JournalInformations
from app.utilities.string_utilities import normalize_string


class OpenAlexReferencesConverter(AbstractReferencesConverter):
    """
    Converts raw data from OpenAlex to a normalised Reference object
    """

    REFERENCE_IDENTIFIERS_IGNORE = ["mag"]

    @AbstractReferencesConverter.validate_reference
    async def convert(self, raw_data: JsonRawResult, new_ref: Reference) -> None:
        """
        Convert raw data from Scanr to a normalised Reference object
        :param raw_data: raw data from Scanr
        :param new_ref: Reference object
        :return: None
        """
        json_payload = raw_data.payload

        language = json_payload.get("language", None)
        new_ref.titles.append(self._title(json_payload, language))
        abstract = self._abstract(json_payload, language)
        if abstract is not None:
            new_ref.abstracts.append(abstract)
        new_ref.document_type.append(await self._document_type(json_payload))

        await self._add_contributions(json_payload, new_ref)

        async for concept in self._concepts(json_payload, language):
            new_ref.subjects.append(concept)

        async for reference_identifier in self._add_reference_identifiers(json_payload):
            new_ref.identifiers.append(reference_identifier)

        journal = await self._journal(json_payload)
        if journal:
            issue = await self._issue(json_payload, journal)
            new_ref.issue = issue

        new_ref.page = (
            f"{json_payload.get('biblio', {}).get('first_page', '')}"
            f"-{json_payload.get('biblio', {}).get('last_page', '')}"
        )

        created = json_payload.get("created_date")
        if created:
            new_ref.created = self._date(created)

        issue = json_payload.get("publication_date")
        if issue:
            new_ref.issued = self._date(issue)

    def _harvester(self) -> str:
        return "OpenAlex"

    async def _journal(self, json_payload) -> Journal | None:
        if json_payload.get("primary_location", {}) is None:
            return None
        if json_payload.get("primary_location", {}).get("source", {}) is None:
            return None
        if (
            json_payload.get("primary_location", {}).get("source", {}).get("type", "")
            != "journal"
        ):
            return None
        source_identifier = (
            json_payload.get("primary_location", {}).get("source", {}).get("id", "")
        )
        if source_identifier is None:
            return None
        title = (
            json_payload.get("primary_location", {})
            .get("source", {})
            .get("display_name", "")
        )
        issn_l = (
            json_payload.get("primary_location", {})
            .get("source", {})
            .get("issn_l", None)
        )
        issn = (
            json_payload.get("primary_location", {}).get("source", {}).get("issn", [])
        )

        publisher = (
            json_payload.get("primary_location", {})
            .get("source", {})
            .get("host_organization_name", "")
        )

        journal = await self._get_or_create_journal(
            JournalInformations(
                source=self._harvester(),
                issn=issn,
                issn_l=issn_l,
                source_identifier=source_identifier,
                titles=[title],
                publisher=publisher,
            )
        )

        return journal

    async def _issue(self, json_payload, journal: Journal) -> Issue | None:
        volume = json_payload.get("biblio", {}).get("volume", "")
        number = json_payload.get("biblio", {}).get("issue", "")
        source_identifier = (
            normalize_string("-".join(journal.titles))
            + f"-{volume}-{number}"
            + f"-{self._harvester()}"
        )
        issue = await self._get_or_create_issue(
            IssueInformations(
                source=self._harvester(),
                journal=journal,
                volume=volume,
                number=[number],
                source_identifier=source_identifier,
            )
        )
        return issue

    async def _add_reference_identifiers(self, json_payload: dict) -> str:
        try:
            for id_key in json_payload["ids"]:
                if id_key not in self.REFERENCE_IDENTIFIERS_IGNORE:
                    yield ReferenceIdentifier(
                        type=id_key, value=json_payload["ids"][id_key]
                    )
        except KeyError:
            yield

    async def _add_contributions(self, json_payload: dict, new_ref: Reference) -> None:
        contribution_informations = []
        rank_count = 1
        for author_object in self._value_from_key(
            json_payload, "authorships", default=[]
        ):
            author = author_object.get("author")
            name = author.get("display_name")
            id_open_alex = author.get("id")
            contribution_informations.append(
                AbstractReferencesConverter.ContributionInformations(
                    role=Contribution.Role.AUTHOR.value,
                    identifier=id_open_alex,
                    name=name,
                    rank=rank_count,
                )
            )
            rank_count += 1
        async for contribution in self._contributions(
            contribution_informations=contribution_informations,
            source="open_alex",
        ):
            new_ref.contributions.append(contribution)

    async def _concepts(self, json_payload, language) -> AsyncGenerator[Concept, None]:
        concept_cache = {}

        for concept in self._value_from_key(json_payload, "concepts", []):
            concept_uri = concept.get("wikidata")
            label = concept.get("display_name")

            if concept_uri in concept_cache:
                yield concept_cache[concept_uri]
                continue
            concept_db = await self._get_or_create_concept_by_uri(
                ConceptInformations(
                    uri=concept_uri,
                    label=label,
                    language=language,
                    source=ConceptInformations.ConceptSources.WIKIDATA,
                )
            )
            concept_cache[concept_uri] = concept_db
            yield concept_db

    def _title(self, json_payload, language: str):
        return Title(
            value=self._value_from_key(json_payload, "title", ""), language=language
        )

    def _abstract(self, json_payload, language: str):
        abstract = self._value_from_key(json_payload, "abstract_inverted_index")
        if abstract is None:
            return None
        value = " ".join(abstract.keys())
        return Abstract(value=value, language=language)

    async def _document_type(self, json_payload):
        document_type = self._value_from_key(json_payload, "type")
        uri, label = OpenAlexDocumentTypeConverter().convert(document_type)
        return await self._get_or_create_document_type_by_uri(uri, label)

    def _value_from_key(self, json_payload, key: str, default=None):
        value = json_payload.get(key, default)
        return value if value is not None else default

    def hash_keys(self, harvester_version: Version) -> list[HashKey]:
        return [
            HashKey("id"),
            HashKey("ids"),
            HashKey("title"),
            HashKey("type"),
            HashKey("concepts"),
            HashKey("authorships", sorted=False),
            HashKey("created_date"),
            HashKey("publication_date"),
        ]

    def _date(self, date):
        # Check if is a valid ISO 8601 date
        try:
            if date is None:
                return None
            return isodate.parse_date(date)
        except isodate.ISO8601Error as error:
            logger.error(f"Could not parse date {date} from OpenAlex with error {error}")
            return None
