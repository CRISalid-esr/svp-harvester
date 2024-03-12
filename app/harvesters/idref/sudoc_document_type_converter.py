from app.harvesters.abstract_document_type_converter import (
    AbstractDocumentTypeConverter,
)


class SudocDocumentTypeConverter(AbstractDocumentTypeConverter):
    """
    Converts raw data from Sudoc to a normalised DocumentType object
    """

    RDF_BIBO = "http://purl.org/ontology/bibo/"

    HARVESTER = "Sudoc"

    TYPES_MAPPING = TYPES_MAPPING = {
        f"{RDF_BIBO}Book": (f"{RDF_BIBO}Book", "Book"),
        f"{RDF_BIBO}Thesis": (f"{RDF_BIBO}Thesis", "Thesis"),
    }
