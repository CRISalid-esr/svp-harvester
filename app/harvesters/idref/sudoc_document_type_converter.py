from app.harvesters.abstract_document_type_converter import (
    AbstractDocumentTypeConverter,
)


class SudocDocumentTypeConverter(AbstractDocumentTypeConverter):
    """
    Converts raw data from Sudoc to a normalised DocumentType object
    """

    HARVESTER = "Sudoc"

    TYPES_MAPPING = {"Text": ("URI", "LABEL")}
