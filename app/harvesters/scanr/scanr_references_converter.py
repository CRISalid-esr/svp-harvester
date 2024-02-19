from loguru import logger

from app.db.models.abstract import Abstract
from app.db.models.reference import Reference
from app.db.models.reference_identifier import ReferenceIdentifier
from app.db.models.title import Title
from app.harvesters.abstract_references_converter import AbstractReferencesConverter
from app.harvesters.json_harvester_raw_result import (
    JsonHarvesterRawResult as JsonRawResult,
)
from app.harvesters.scanr.scanr_document_type_converter import (
    ScanrDocumentTypeConverter,
)
from app.harvesters.scanr.scanr_roles_converter import ScanrRolesConverter
from app.services.concepts.concept_informations import ConceptInformations


class ScanrReferencesConverter(AbstractReferencesConverter):
    """
    Converts raw data from ScanR to a normalised Reference object
    """

    PREFERRED_LANGUAGE = "fr"

    IDENTIFIERS_TO_IGNORE = ["scanr"]

    @AbstractReferencesConverter.validate_reference
    async def convert(self, raw_data: JsonRawResult, new_ref: Reference) -> None:
        """
        Convert raw data from Scanr to a normalised Reference object
        :param raw_data: raw data from Scanr
        :param new_ref: Reference object
        :return: None
        """
        json_payload = raw_data.payload

        title = json_payload["_source"].get("title")
        if title:
            new_ref.titles.extend(
                self._remove_duplicates_from_language_data(title, Title)
            )

        summary = json_payload["_source"].get("summary")
        if summary:
            new_ref.abstracts.extend(
                self._remove_duplicates_from_language_data(summary, Abstract)
            )

        document_type_code = json_payload["_source"].get("type")
        if document_type_code:
            new_ref.document_type.append(await self._document_type(document_type_code))

        domains = json_payload["_source"].get("domains")
        if domains:
            async for subject in self._concepts(domains):
                new_ref.subjects.append(subject)

        await self._add_contributions(json_payload, new_ref)

        for identifier in self._add_identifiers(json_payload):
            new_ref.identifiers.append(identifier)

    def _harvester(self) -> str:
        return "ScanR"

    def _add_identifiers(self, json_payload: dict) -> ReferenceIdentifier:
        external_ids = json_payload["_source"].get("externalIds", [])
        for identifier in external_ids:
            if identifier["type"] not in self.IDENTIFIERS_TO_IGNORE:
                yield ReferenceIdentifier(
                    value=identifier["id"], type=identifier["type"]
                )

    async def _add_contributions(self, json_payload: dict, new_ref: Reference) -> None:
        raw_contributions = json_payload["_source"].get("authors")
        contribution_informations = [
            AbstractReferencesConverter.ContributionInformations(
                role=ScanrRolesConverter.convert(
                    role=contribution.get("role"),
                ),
                name=contribution.get("fullName"),
                identifier=contribution.get("person"),
                rank=rank,
            )
            for rank, contribution in enumerate(raw_contributions)
        ]
        async for contribution in self._contributions(
            contribution_informations=contribution_informations, source="scanr"
        ):
            new_ref.contributions.append(contribution)

    @staticmethod
    def _remove_duplicates_from_language_data(language_data: dict, model_class):
        processed_items = [
            model_class(value=value, language=key)
            for key, value in language_data.items()
            if key != "default"
        ]

        default_item = language_data.get("default")

        if default_item:
            if not any(item for item in processed_items if item.value == default_item):
                processed_items.append(model_class(value=default_item, language=None))

        return processed_items

    async def _document_type(self, code_document_type: str):
        uri, label = ScanrDocumentTypeConverter.convert(code_document_type)
        return await self._get_or_create_document_type_by_uri(uri, label)

    async def _concepts(self, domains):
        concept_cache = {}

        for subject in domains:
            concept_id = subject.get("code")

            concept_type = subject.get("type")
            concept_source = self._get_concept_source(concept_type)

            label_dict = subject.get("label", {})
            concept_label, concept_language = self._get_concept_label(label_dict)

            if concept_id in concept_cache:
                yield concept_cache[concept_id]
                continue
            concept_db = await self._get_or_create_concept_by_uri(
                ConceptInformations(
                    uri=concept_id,
                    label=concept_label,
                    language=concept_language,
                    source=concept_source,
                )
            )
            concept_cache[concept_id] = concept_db
            yield concept_db

    @staticmethod
    def _get_concept_source(concept_type):
        source_mapping = {
            "wikidata": ConceptInformations.ConceptSources.WIKIDATA,
            "sudoc": ConceptInformations.ConceptSources.IDREF,
            "keyword": None,
        }
        if concept_type not in source_mapping:
            logger.warning(f"Unknown Scanr subject type: {concept_type}")

        concept_source = source_mapping.get(concept_type)

        return concept_source

    def _get_concept_label(self, label_dict):
        concept_label = label_dict.get(self.PREFERRED_LANGUAGE)
        if concept_label is not None:
            concept_language = self.PREFERRED_LANGUAGE
        else:
            concept_label, concept_language = self._get_non_default_label(label_dict)
        return concept_label, concept_language

    @staticmethod
    def _get_non_default_label(label_dict):
        for language, value in label_dict.items():
            if language != "default":
                return value, language
        return label_dict.get("default"), None

    def hash_keys(self):
        # This listing is independant of PUBLICATIONS_DEFAULT_FIELDS
        # in ScanRApiQueryBuilder
        # pylint: disable=duplicate-code
        return [
            "id",
            "title",
            "summary",
            "type",
            "productionType",
            "publicationDate",
            "domains",
            "affiliations",
            "authors",
            "externalIds",
        ]
