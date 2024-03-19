from app.harvesters.abstract_document_type_converter import (
    AbstractDocumentTypeConverter,
)


class SciencePlusDocumentTypeConverter(AbstractDocumentTypeConverter):
    """
    Converts raw data from SciencePlus to a normalised DocumentType object
    """

    HARVESTER = "SciencePlus"

    RDF = AbstractDocumentTypeConverter.RDF

    TYPES_MAPPING = {
        f"{RDF['RDA']}C10001": (
            f"{RDF['RDA']}C10001",
            "Work",
        ),
        f"{RDF['BIBO']}Article": (
            f"{RDF['BIBO']}Article",
            "Article",
        ),
    }
