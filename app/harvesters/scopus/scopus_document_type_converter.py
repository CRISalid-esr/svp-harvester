from app.harvesters.abstract_document_type_converter import (
    AbstractDocumentTypeConverter,
)


class ScopusDocumentTypeConverter(AbstractDocumentTypeConverter):
    """
    Document type converter for Scopus
    """

    HARVESTER = "Scopus"

    TYPES_MAPPING = {
        "ed": ("http://data.crisalid.org/ref/document_types/unknown", "Editorial"),
        "ar": ("http://data.crisalid.org/ref/document_types/unknown", "Article"),
        "re": ("http://data.crisalid.org/ref/document_types/unknown", "Review"),
        "ch": ("http://data.crisalid.org/ref/document_types/unknown", "Book Chapter"),
        "cp": (
            "http://data.crisalid.org/ref/document_types/unknown",
            "Conference Paper",
        ),
        "bk": ("http://data.crisalid.org/ref/document_types/unknown", "Book"),
        "er": ("http://data.crisalid.org/ref/document_types/unknown", "Erratum"),
    }
