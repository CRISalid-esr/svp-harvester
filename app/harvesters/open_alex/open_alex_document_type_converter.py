from app.harvesters.abstract_document_type_converter import (
    AbstractDocumentTypeConverter,
)


class OpenAlexDocumentTypeConverter(AbstractDocumentTypeConverter):
    """
    Use mapping table ton convert hal document type values to loc document type values
    """

    RDF_BIBO = "http://purl.org/ontology/bibo/"
    RDF_SPAR = "http://purl.org/spar/fabio/"
    RDF_COAR = "http://purl.org/coar/resource_type/"
    RDF_CERIF = "http://purl.org/cerif/frapo/"

    HARVESTER = "OPEN_ALEX"

    TYPES_MAPPING = {
        "article": (f"{RDF_BIBO}Article", "Article"),
        "book": (f"{RDF_BIBO}Book", "Book"),
        "book-chapter": (f"{RDF_BIBO}Chapter", "Chapter"),
        "dataset": (f"{RDF_SPAR}Dataset", "Dataset"),
        "dissertation": (f"{RDF_BIBO}Thesis", "Thesis"),
        "editorial": (f"{RDF_SPAR}Editorial", "Editorial"),
        "erratum": (f"{RDF_SPAR}Erratum", "Erratum"),
        "grant": (f"{RDF_CERIF}Grant", "Grant"),
        "letter": (f"{RDF_BIBO}Letter", "Letter"),
        "other": (f"{RDF_COAR}c_1843", "Other"),
        "paratext": (f"{RDF_SPAR}MetadataDocument", "Metadata Document"),
        "peer-review": ("Peer review URI", "Peer review"),
        "reference-entry": ("Reference entry URI", "Reference entry"),
        "report": (f"{RDF_SPAR}Report", "Report"),
        "standard": (f"{RDF_BIBO}Standard", "Standard"),
    }
