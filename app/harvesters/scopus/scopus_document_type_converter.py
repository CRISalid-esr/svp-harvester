from app.harvesters.abstract_document_type_converter import (
    AbstractDocumentTypeConverter,
)


class ScopusDocumentTypeConverter(AbstractDocumentTypeConverter):
    """
    Document type converter for Scopus
    """

    HARVESTER = "Scopus"

    BIBO_NAMESPACE = "http://purl.org/ontology/bibo/"
    FABIO_NAMESPACE = "http://purl.org/spar/fabio/"
    COAR_NAMESPACE = "http://purl.org/coar/resource_type/"

    TYPES_MAPPING = {
        "ar": (f"{BIBO_NAMESPACE}Article", "Article"),
        "ed": (f"{FABIO_NAMESPACE}Editorial", "Editorial"),
        "re": (f"{FABIO_NAMESPACE}ReviewPaper", "Review"),
        "ch": (f"{BIBO_NAMESPACE}Chapter", "Chapter"),
        "bk": (f"{BIBO_NAMESPACE}Book", "Book"),
        "er": (f"{FABIO_NAMESPACE}Erratum", "Erratum"),
        "le": (f"{BIBO_NAMESPACE}Letter", "Letter"),
        "ot": (f"{COAR_NAMESPACE}c_1843", "Other"),
        "no": ("http://data.crisalid.org/ref/document_types/unknown", "Note"),
        "sh": ("http://data.crisalid.org/ref/document_types/unknown", "Short Survey"),
        "dp": ("http://data.crisalid.org/ref/document_types/unknown", "Data Paper"),
        "aip": (
            "http://data.crisalid.org/ref/document_types/unknown",
            "Article in Press",
        ),
        "cp": (
            "http://data.crisalid.org/ref/document_types/unknown",
            "Conference Paper",
        ),
        "cr": (
            "http://data.crisalid.org/ref/document_types/unknown",
            "Conference Review",
        ),
    }
