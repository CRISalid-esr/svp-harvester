from app.harvesters.abstract_document_type_converter import (
    AbstractDocumentTypeConverter,
)


class IdrefDocumentTypeConverter(AbstractDocumentTypeConverter):
    """
    Document type converter for IdRef Sparql harvester
    """

    HARVESTER = "IDREF"

    TYPES_MAPPING = {
        "http://purl.org/vocab/frbr/core#Work": (
            "http://purl.org/vocab/frbr/core#Work",
            "Work",
        ),
        "http://rdaregistry.info/Elements/c/C10001": ("URI", "LABEL"),
    }
