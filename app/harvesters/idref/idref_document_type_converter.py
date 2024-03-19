from app.harvesters.abstract_document_type_converter import (
    AbstractDocumentTypeConverter,
)


class IdrefDocumentTypeConverter(AbstractDocumentTypeConverter):
    """
    Document type converter for IdRef Sparql harvester
    """

    HARVESTER = "IDREF"
    RDF = AbstractDocumentTypeConverter.RDF

    TYPES_MAPPING = {
        f"{RDF['FRBR']}Work": (
            f"{RDF['FRBR']}Work",
            "Work",
        ),
        f"{RDF['RDA']}C10001": (
            f"{RDF['RDA']}C10001",
            "Work",
        ),
    }
