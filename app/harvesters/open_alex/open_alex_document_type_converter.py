from app.harvesters.abstract_document_type_converter import (
    AbstractDocumentTypeConverter,
)


class OpenAlexDocumentTypeConverter(AbstractDocumentTypeConverter):
    """
    Use mapping table ton convert hal document type values to loc document type values
    """

    HARVESTER = "OPEN_ALEX"

    TYPES_MAPPING = {
        "article": ("Article URI", "Article"),
        "book-chapter": ("Book chapter URI", "Book chapter"),
        "dissertation": ("Dissertation URI", "Dissertation"),
        "book": ("Book URI", "Book"),
        "dataset": ("Dataset URI", "Dataset"),
        "paratext": ("Paratext URI", "Paratext"),
        "other": ("Other URI", "Other"),
        "reference-entry": ("Reference entry URI", "Reference entry"),
        "report": ("Report URI", "Report"),
        "peer-review": ("Peer review URI", "Peer review"),
        "standard": ("Standard URI", "Standard"),
        "editorial": ("Editorial URI", "Editorial"),
        "erratum": ("Erratum URI", "Erratum"),
        "grant": ("Grant URI", "Grant"),
        "letter": ("Letter URI", "Letter"),
    }
