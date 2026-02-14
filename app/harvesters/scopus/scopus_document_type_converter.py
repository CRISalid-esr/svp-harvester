from app.harvesters.abstract_document_type_converter import (
    AbstractDocumentTypeConverter,
)


class ScopusDocumentTypeConverter(AbstractDocumentTypeConverter):
    """
    Document type converter for Scopus
    """

    BIBO_NAMESPACE = "http://purl.org/ontology/bibo/"
    FABIO_NAMESPACE = "http://purl.org/spar/fabio/"
    COAR_NAMESPACE = "http://purl.org/coar/resource_type/"

    TYPES_MAPPING = {
        "aip": (
            "http://data.crisalid.org/ref/document_types/unknown",
            "Article in Press",
        ),
        "ar": (f"{BIBO_NAMESPACE}Article", "Article"),
        "bk": (f"{BIBO_NAMESPACE}Book", "Book"),
        "ch": (f"{BIBO_NAMESPACE}Chapter", "Chapter"),
        "cp": (
            "http://data.crisalid.org/ref/document_types/unknown",
            "Conference Paper",
        ),
        "cr": (
            "http://data.crisalid.org/ref/document_types/unknown",
            "Conference Review",
        ),
        "dp": ("http://data.crisalid.org/ref/document_types/unknown", "Data Paper"),
        "ed": (f"{FABIO_NAMESPACE}Editorial", "Editorial"),
        "er": (f"{FABIO_NAMESPACE}Erratum", "Erratum"),
        "le": (f"{BIBO_NAMESPACE}Letter", "Letter"),
        "no": ("http://data.crisalid.org/ref/document_types/unknown", "Note"),
        "ot": (f"{COAR_NAMESPACE}c_1843", "Other"),
        "re": (f"{FABIO_NAMESPACE}ReviewPaper", "Review"),
        "sh": ("http://data.crisalid.org/ref/document_types/unknown", "Short Survey"),
    }
