from loguru import logger


class OpenEditionDocumentTypeConverter:
    """
    Use mapping table to convert Open Edition document type to loc document type values
    """

    RDF_BIBO = "http://purl.org/ontology/bibo/"
    RDF_SPAR = "http://purl.org/spar/fabio/"
    RDF_COAR = "http://purl.org/coar/resource_type"

    CODES_MAPPING = {
        "article": (f"{RDF_BIBO}Article", "Article"),
        "introduction": (f"{RDF_BIBO}Chapter", "Chapter"),
        "review": (f"{RDF_BIBO}Article", "Article"),
        "archaelogical note": (f"{RDF_BIBO}Note", "Note"),
    }

    UKNOWN_CODE = ("http://data.crisalid.org/ref/document_types/unkown", "Uknown")

    @staticmethod
    def convert(type_document: str) -> tuple[str, str]:
        """
        Given an Open Edition document type, return the corresponding loc document type
        """
        if type_document not in OpenEditionDocumentTypeConverter.CODES_MAPPING:
            logger.warning(
                f"Unknown Open Edition document type: {type_document}",
            )
            return OpenEditionDocumentTypeConverter.UKNOWN_CODE

        return OpenEditionDocumentTypeConverter.CODES_MAPPING[type_document]
