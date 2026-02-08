from abc import ABC

from loguru import logger


class AbstractDocumentTypeConverter(ABC):
    """
    Abstract mother class for all document type converters.
    """

    RDF = {
        "BIBO": "http://purl.org/ontology/bibo/",
        "CERIF": "http://purl.org/cerif/frapo/",
        "COAR": "http://purl.org/coar/resource_type/",
        "FRBR": "http://purl.org/vocab/frbr/core#",
        "RDA": "http://rdaregistry.info/Elements/c/",
        "SPAR": "http://purl.org/spar/fabio/",
    }

    UNKNOWN_CODE = ("http://data.crisalid.org/ref/document_types/unknown", "Unknown")

    TYPES_MAPPING: dict[str, tuple[str, str]]

    def __init__(self) -> None:
        self.types_mapping = self.TYPES_MAPPING

    def convert(self, document_type: str) -> tuple[str, str]:
        """
        Given a document type, return the corresponding loc document type
        :param document_type: document type

        :return: Uri and label of the document type
        """
        if document_type not in self.types_mapping:
            logger.warning(
                f"Unknown document type: {document_type} in concrete "
                f"class {self.__class__.__name__}"
            )
            return self.UNKNOWN_CODE
        return self.TYPES_MAPPING[document_type]
