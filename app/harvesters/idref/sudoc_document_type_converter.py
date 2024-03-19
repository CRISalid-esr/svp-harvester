from app.harvesters.abstract_document_type_converter import (
    AbstractDocumentTypeConverter,
)


class SudocDocumentTypeConverter(AbstractDocumentTypeConverter):
    """
    Converts raw data from Sudoc to a normalised DocumentType object
    """

    HARVESTER = "Sudoc"

    RDF = AbstractDocumentTypeConverter.RDF

    TYPES_MAPPING = {
        f"{RDF['BIBO']}Book": (
            f"{RDF['BIBO']}Book",
            "Book",
        ),
        f"{RDF['BIBO']}Thesis": (
            f"{RDF['BIBO']}Thesis",
            "Thesis",
        ),
    }
