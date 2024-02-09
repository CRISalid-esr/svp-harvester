from app.db.models.abstract import Abstract
from app.db.models.reference_identifier import ReferenceIdentifier
from app.db.models.reference import Reference
from app.db.models.title import Title
from app.harvesters.abstract_references_converter import AbstractReferencesConverter
from app.harvesters.json_harvester_raw_result import (
    JsonHarvesterRawResult as JsonRawResult,
)
from app.harvesters.scanr.scanr_document_type_converter import (
    ScanrDocumentTypeConverter,
)
from app.harvesters.scanr.scanr_roles_converter import ScanrRolesConverter


class ScanrReferencesConverter(AbstractReferencesConverter):
    """
    Converts raw data from ScanR to a normalised Reference object
    """

    IDENTIFIERS_TO_IGNORE = ["scanr"]

    async def convert(self, raw_data: JsonRawResult) -> Reference:
        """
        Convert raw data from ScanR to a normalised Reference object
        :param raw_data: raw data from ScanR
        :return: Reference object
        """
        new_ref = Reference()

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

        await self._add_contributions(json_payload, new_ref)

        for identifier in self._add_identifiers(json_payload):
            new_ref.identifiers.append(identifier)

        new_ref.hash = self._hash(json_payload)
        new_ref.harvester = "scanR"
        new_ref.source_identifier = json_payload["_source"].get("id")
        return new_ref

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
            for rank, contribution in zip(
                range(0, len(raw_contributions)), raw_contributions
            )
        ]
        async for contribution in self._contributions(
            contribution_informations=contribution_informations, source="scanr"
        ):
            new_ref.contributions.append(contribution)

    def _remove_duplicates_from_language_data(self, language_data: dict, model_class):
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

    def _hash_keys(self):
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
