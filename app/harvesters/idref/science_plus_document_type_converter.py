from app.harvesters.abstract_document_type_converter import (
    AbstractDocumentTypeConverter,
)


class SciencePlusDocumentTypeConverter(AbstractDocumentTypeConverter):
    """
    Converts raw data from SciencePlus to a normalised DocumentType object
    """

    HARVESTER = "SciencePlus"

    TYPES_MAPPING = {
        "http://rdaregistry.info/Elements/c/C10001": ("URI", "LABEL"),
        "http://purl.org/ontology/bibo/Article": (
            "http://purl.org/ontology/bibo/Article",
            "Article",
        ),
    }
