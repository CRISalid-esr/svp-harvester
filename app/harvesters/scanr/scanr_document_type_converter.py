from loguru import logger


class ScanrDocumentTypeConverter:
    """
    Use mapping table ton convert scanr document type values to loc document type values
    """

    RDF_BIBO = "http://purl.org/ontology/bibo/"
    RDF_SPAR = "http://purl.org/spar/fabio/"
    RDF_COAR = "http://purl.org/coar/resource_type"

    # TODO: update thesis when the mapping is confirmed
    CODES_MAPPING = {
        "book": (f"{RDF_BIBO}Book", "Book"),
        "book-chapter": (f"{RDF_BIBO}Chapter", "Chapter"),
        "journal-article": (f"{RDF_BIBO}Article", "Article"),
        "other": (f"{RDF_COAR}c_1843", "Other"),
        "preprint": (f"{RDF_SPAR}Preprint", "Preprint"),
        "proceedings": (f"{RDF_BIBO}Proceedings", "Proceedings"),
        "these": (f"{RDF_BIBO}Thesis", "Thesis"),
        "thesis": (f"{RDF_BIBO}Thesis", "Thesis"),
    }

    UNKNOWN_CODE = ("http://data.crisalid.org/ref/document_types/unknown", "Unknown")

    @staticmethod
    def convert(code: str) -> tuple[str, str]:
        """
        Given a SCANR document type code, return the corresponding uri and label
        """
        if code not in ScanrDocumentTypeConverter.CODES_MAPPING:
            logger.warning(
                f"Unknown SCANR document type code: {code}",
            )
            return ScanrDocumentTypeConverter.UNKNOWN_CODE

        return ScanrDocumentTypeConverter.CODES_MAPPING[code]
