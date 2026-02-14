from app.harvesters.abstract_document_type_converter import (
    AbstractDocumentTypeConverter,
)


class SciencePlusDocumentTypeConverter(AbstractDocumentTypeConverter):
    """
    Converts raw data from SciencePlus to a normalised DocumentType object
    """

    RDF = AbstractDocumentTypeConverter.RDF

    TYPES_MAPPING = {
        f"{RDF['BIBO']}Article": (
            f"{RDF['BIBO']}Article",
            "Article",
        ),
        f"{RDF['RDA']}C10001": (
            f"{RDF['RDA']}C10001",
            "Work",
        ),
    }
