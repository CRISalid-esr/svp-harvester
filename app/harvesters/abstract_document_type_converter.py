from abc import ABC

from loguru import logger

UNKNOWN_CODE = ("http://data.crisalid.org/ref/document_types/unknown", "Unknown")


class AbstractDocumentTypeConverter(ABC):
    """
    Abstract mother class for all document type converters.
    """

    HARVESTER: str

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
            return UNKNOWN_CODE
        return self.types_mapping[document_type]
