from abc import ABC

from loguru import logger


class AbstractDocumentTypeConverter(ABC):
    """
    Abstract mother class for all document type converters.
    """

    HARVESTER: str

    RDF = {
        "BIBO": "http://purl.org/ontology/bibo/",
        "SPAR": "http://purl.org/spar/fabio/",
        "COAR": "http://purl.org/coar/resource_type/",
        "CERIF": "http://purl.org/cerif/frapo/",
        "FRBR": "http://purl.org/vocab/frbr/core#",
        "RDA": "http://rdaregistry.info/Elements/c/",
    }

    UNKNOWN_CODE = ("http://data.crisalid.org/ref/document_types/unknown", "Unknown")

    TYPES_MAPPING: dict[str, tuple[str, str]]

    def __init__(self) -> None:
        self.harvester = self.HARVESTER
        self.types_mapping = self.TYPES_MAPPING

    def convert(self, document_type: str) -> tuple[str, str]:
        """
        Given a document type, return the corresponding loc document type
        :param document_type: document type

        :return: Uri and label of the document type
        """
        if document_type not in self.types_mapping:
            logger.warning(f"Unknown {self.harvester} document type: {document_type}")
            return self.UNKNOWN_CODE
        return self.TYPES_MAPPING[document_type]
