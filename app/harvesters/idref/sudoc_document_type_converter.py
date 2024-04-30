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
        f"{RDF['BIBO']}Article": (f"{RDF['BIBO']}Article", "Article"),
        f"{RDF['BIBO']}Document": (f"{RDF['BIBO']}Document", "Document"),
        f"{RDF['BIBO']}Excerpt": (f"{RDF['BIBO']}Excerpt", "Excerpt"),
    }
