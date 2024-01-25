from app.harvesters.abstract_document_type_converter import (
    AbstractDocumentTypeConverter,
)


class OpenAlexDocumentTypeConverter(AbstractDocumentTypeConverter):
    """
    Use mapping table ton convert hal document type values to loc document type values
    """

    HARVESTER = "OPEN_ALEX"

    # TODO COMPLETE MAPPING TABLE
    TYPES_MAPPING = {
        "article": ("Article", "Article"),
        "erratum": ("Erratum", "Erratum"),
    }
