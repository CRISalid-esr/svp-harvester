from xml.etree.ElementTree import Element
import isodate
from loguru import logger
from app.db.models.reference import Reference
from app.db.models.reference_identifier import ReferenceIdentifier
from app.db.models.title import Title
from app.harvesters.abstract_references_converter import AbstractReferencesConverter
from app.harvesters.scopus.scopus_client import ScopusClient
from app.harvesters.scopus.scopus_document_type_converter import (
    ScopusDocumentTypeConverter,
)
from app.harvesters.xml_harvester_raw_result import XMLHarvesterRawResult


class ScopusReferencesConverter(AbstractReferencesConverter):
    """
    Converts raw data from Scopus API to a normalised Reference Object
    """

    FIELD_NAME_IDENTIFIER = {
        "prism:issn": "issn",
        "prism:isbn": "isbn",
        "prism:doi": "doi",
        "default:pubmed-id": "pubmed",
    }

    @AbstractReferencesConverter.validate_reference
    async def convert(
        self, raw_data: XMLHarvesterRawResult, new_ref: Reference
    ) -> None:
        entry: Element = raw_data.payload

        async for title in self._title(entry):
            new_ref.titles.append(title)

        async for document_type in self._document_type(entry):
            new_ref.document_type.append(document_type)

        async for identifier in self._indetifiers(entry):
            new_ref.identifiers.append(identifier)

        new_ref.issued = self._issued(entry)

    async def _document_type(self, entry: Element):
        for document_type in self._get_elements(entry, "default:subtype"):
            uri, label = ScopusDocumentTypeConverter().convert(document_type.text)
            yield await self._get_or_create_document_type_by_uri(uri=uri, label=label)

    async def _indetifiers(self, entry: Element):
        for key_identifier, type_identifier in self.FIELD_NAME_IDENTIFIER.items():
            identifier = self._get_element(entry, key_identifier)
            if identifier is not None:
                yield ReferenceIdentifier(
                    type=type_identifier,
                    value=identifier.text,
                )

    async def _title(self, entry: Element):
        for title in self._get_elements(entry, "dc:title"):
            yield Title(value=title.text)

    def _issued(self, entry: Element):
        issued = self._get_element(entry, "prism:coverDate")
        return self._date(issued.text)

    def _get_element(self, entry: Element, tag: str) -> Element:
        return entry.find(tag, ScopusClient.NAMESPACE)

    def _get_elements(self, entry: Element, tag: str) -> list[Element]:
        return entry.findall(tag, ScopusClient.NAMESPACE)

    def _date(self, date):
        try:
            if date is None:
                return None
            return isodate.parse_date(date)
        except isodate.ISO8601Error as error:
            logger.error(f"Could not parse date {date} from Scopus with error {error}")
            return None

    def _harvester(self) -> str:
        return "Scopus"

    # TODO Completar, con nuevo hash ?
    def hash_keys(self) -> list[str]:
        return []
