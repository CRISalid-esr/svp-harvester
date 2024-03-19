from app.harvesters.abstract_document_type_converter import (
    AbstractDocumentTypeConverter,
)


class ScanrDocumentTypeConverter(AbstractDocumentTypeConverter):
    """
    Use mapping table ton convert scanr document type values to loc document type values
    """

    HARVESTER = "SCANR"

    RDF = AbstractDocumentTypeConverter.RDF

    TYPES_MAPPING = {
        "book": (f"{RDF['BIBO']}Book", "Book"),
        "book-chapter": (f"{RDF['BIBO']}Chapter", "Chapter"),
        "journal-article": (f"{RDF['BIBO']}Article", "Article"),
        "other": (f"{RDF['COAR']}c_1843", "Other"),
        "preprint": (f"{RDF['SPAR']}Preprint", "Preprint"),
        "proceedings": (f"{RDF['BIBO']}Proceedings", "Proceedings"),
        "these": (f"{RDF['BIBO']}Thesis", "Thesis"),
        "thesis": (f"{RDF['BIBO']}Thesis", "Thesis"),
    }
