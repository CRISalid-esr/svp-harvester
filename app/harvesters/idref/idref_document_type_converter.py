from app.harvesters.abstract_document_type_converter import (
    AbstractDocumentTypeConverter,
)


class IdrefDocumentTypeConverter(AbstractDocumentTypeConverter):
    """
    Document type converter for IdRef Sparql harvester
    """

    RDF_FRBR = "http://purl.org/vocab/frbr/core#"
    RDF_RDA = "http://rdaregistry.info/Elements/c/"

    HARVESTER = "IDREF"

    TYPES_MAPPING = {
        f"{RDF_FRBR}Work": (f"{RDF_FRBR}Work", "Work"),
        f"{RDF_RDA}C10001": (f"{RDF_RDA}C10001", "Work"),
    }
