from app.db.models.abstract import Abstract
from app.db.models.reference import Reference
from app.db.models.title import Title
from app.harvesters.abstract_references_converter import AbstractReferencesConverter
from app.harvesters.json_harvester_raw_result import (
    JsonHarvesterRawResult as JsonRawResult,
)


class ScanrReferencesConverter(AbstractReferencesConverter):
    """
    Converts raw data from ScanR to a normalised Reference object
    """

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
            new_ref.titles.extend(self._remove_duplicates_from_language_data(title, Title))

        summary = json_payload["_source"].get("summary")
        if summary:
            new_ref.abstracts.extend(self._remove_duplicates_from_language_data(summary, Abstract))

        new_ref.hash = self._hash(json_payload)
        new_ref.harvester = "scanR"
        new_ref.source_identifier = json_payload["_source"].get("id")
        return new_ref

    def _remove_duplicates_from_language_data(self, language_data: dict, model_class):

        processed_items = [
            model_class(value=value, language=key)
            for key, value in language_data.items() if key != "default"
        ]

        default_item = language_data.get("default")

        if default_item:

            if not any(item for item in processed_items if item.value == default_item):
                processed_items.append(model_class(value=default_item, language=None))

        return processed_items

    def _hash_keys(self):
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
