from app.harvesters.abstract_document_type_converter import (
    AbstractDocumentTypeConverter,
)


class OpenEditionDocumentTypeConverter(AbstractDocumentTypeConverter):
    """
    Use mapping table to convert Open Edition document type to loc document type values
    """

    HARVESTER = "Open_Edition"

    RDF = AbstractDocumentTypeConverter.RDF

    TYPES_MAPPING = {
        "article": (f"{RDF['BIBO']}Article", "Article"),
        "introduction": (f"{RDF['BIBO']}Chapter", "Chapter"),
        "review": (f"{RDF['BIBO']}Article", "Article"),
        "archaelogical note": (f"{RDF['BIBO']}Note", "Note"),
        "chapter": (f"{RDF['BIBO']}Chapter", "Chapter"),
    }
