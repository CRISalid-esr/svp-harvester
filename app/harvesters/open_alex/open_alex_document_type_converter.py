from app.harvesters.abstract_document_type_converter import (
    AbstractDocumentTypeConverter,
)


class OpenAlexDocumentTypeConverter(AbstractDocumentTypeConverter):
    """
    Use mapping table ton convert hal document type values to loc document type values
    """

    HARVESTER = "OPENALEX"

    RDF = AbstractDocumentTypeConverter.RDF

    TYPES_MAPPING = {
        "article": (f"{RDF['BIBO']}Article", "Article"),
        "book": (f"{RDF['BIBO']}Book", "Book"),
        "book-chapter": (f"{RDF['BIBO']}Chapter", "Chapter"),
        "dataset": (f"{RDF['SPAR']}Dataset", "Dataset"),
        "dissertation": (f"{RDF['BIBO']}Thesis", "Thesis"),
        "editorial": (
            f"{RDF['SPAR']}Editorial",
            "Editorial",
        ),
        "erratum": (f"{RDF['SPAR']}Erratum", "Erratum"),
        "grant": (f"{RDF['CERIF']}Grant", "Grant"),
        "letter": (f"{RDF['BIBO']}Letter", "Letter"),
        "other": (f"{RDF['COAR']}c_1843", "Other"),
        "paratext": (
            f"{RDF['SPAR']}MetadataDocument",
            "Metadata Document",
        ),
        "peer-review": ("Peer review URI", "Peer review"),
        "reference-entry": ("Reference entry URI", "Reference entry"),
        "report": (f"{RDF['SPAR']}Report", "Report"),
        "standard": (f"{RDF['BIBO']}Standard", "Standard"),
        "preprint": (f"{RDF['SPAR']}Preprint", "Preprint"),
    }
