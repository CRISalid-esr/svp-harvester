from loguru import logger


class OpenAlexDocumentTypeConverter:
    """
    Use mapping table ton convert hal document type values to loc document type values
    """

    # TODO COMPLETE MAPPING TABLE
    CODES_MAPPING = {"article": ("Article", "Article")}

    UNKNOWN_CODE = ("http://data.crisalid.org/ref/document_types/unknown", "Unknown")

    @staticmethod
    def convert(document_type: str) -> tuple[str, str]:
        """
        Given a OpenAlex document type, return the corresponding loc document type
        """
        if document_type not in OpenAlexDocumentTypeConverter.CODES_MAPPING:
            logger.warning(f"Unknown OpenAlex document type: {document_type}")
            return OpenAlexDocumentTypeConverter.UNKNOWN_CODE

        return OpenAlexDocumentTypeConverter.CODES_MAPPING[document_type]
