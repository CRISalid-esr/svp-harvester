from app.harvesters.abstract_document_type_converter import (
    AbstractDocumentTypeConverter,
)


class SciencePlusDocumentTypeConverter(AbstractDocumentTypeConverter):
    """
    Converts raw data from SciencePlus to a normalised DocumentType object
    """

    RDF_BIBO = "http://purl.org/ontology/bibo/"
    RDF_RDA = "http://rdaregistry.info/Elements/c/"

    HARVESTER = "SciencePlus"

    TYPES_MAPPING = {
        f"{RDF_RDA}C10001": (f"{RDF_RDA}C10001", "Work"),
        f"{RDF_BIBO}Article": (f"{RDF_BIBO}Article", "Article"),
    }
