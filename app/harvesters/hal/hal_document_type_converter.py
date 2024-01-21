from loguru import logger


class HalDocumentTypeConverter:
    """
    Use mapping table ton convert hal document type values to loc document type values
    """

    RDF_BIBO = "http://purl.org/ontology/bibo/"
    RDF_SPAR = "http://purl.org/spar/fabio/"
    RDF_COAR = "http://purl.org/coar/resource_type"

    CODES_MAPPING = {
        "ART": (f"{RDF_BIBO}Article", "Article"),
        "COMM": (f"{RDF_SPAR}ConferencePaper", "Conference Paper"),
        "COUV": (f"{RDF_BIBO}Chapter", "Chapter"),
        "THESE": (f"{RDF_BIBO}Thesis", "Thesis"),
        "OUV": (f"{RDF_BIBO}Book", "Book"),
        "UNDEFINDED": (f"{RDF_SPAR}Preprint", "Preprint"),
        "MEM": (
            "https://vocabularies.coar-repositories.org/resource_types/c_bdcc/",
            "Master Thesis",
        ),
        "OTHER": (f"{RDF_COAR}c_1843", "Other"),
        "REPORT": (f"{RDF_SPAR}Report", "Report"),
        "IMG": (f"{RDF_SPAR}Image", "Image"),
        "POSTER": (f"{RDF_SPAR}ConferencePoster", "Conference Poster"),
        "ISSUE": (f"{RDF_BIBO}Document", "Document"),
        "NOTICE": (f"{RDF_BIBO}Document", "Document"),
        "PROCEEDING": (f"{RDF_BIBO}Proceedings", "Proceedings"),
        "HRD": (f"{RDF_BIBO}Document", "Document"),
        "BLOG": (f"{RDF_COAR}c_6947", "Blog Post"),
        "PATENT": (f"{RDF_BIBO}Patent", "Patent"),
        "REPORT_LABO": (f"{RDF_COAR}c_93fc", "Report"),
        "VIDEO": (
            f"{RDF_BIBO}AudioVisualDocument",
            "Audiovisual Document",
        ),
        "REPORT_MAST": (f"{RDF_COAR}c_93fc", "Report"),
        "LECTURE": (f"{RDF_COAR}c_8544", "Lecture"),
        "REPORT_LPRO": (f"{RDF_COAR}c_93fc", "Report"),
        "REPORT_LICE": (f"{RDF_COAR}c_93fc", "Report"),
        "TRAD": (f"{RDF_COAR}c_1843", "Other"),
        "SOFTWARE": (f"{RDF_COAR}c_5ce6", "Software"),
        "PRESCONF": (f"{RDF_COAR}c_c94f", "Conference Output"),
        "CREPORT": (f"{RDF_COAR}c_93fc", "Report"),
        "REPORT_DOCT": (f"{RDF_COAR}c_93fc", "Report"),
        "REPORT_ETAB": (f"{RDF_COAR}c_93fc", "Report"),
        "MAP": (f"{RDF_BIBO}Map", "Map"),
        "REPORTFORM": (f"{RDF_COAR}c_93fc", "Report"),
        "OTHERREPORT": (f"{RDF_COAR}c_18wq", "Report"),
        "NOTE": (f"{RDF_BIBO}Note", "Note"),
        "SYNTHESE": (f"{RDF_BIBO}Document", "Document"),
        "REPORT_FPROJ": (f"{RDF_COAR}c_93fc", "Report"),
        "REPORT_GLICE": (f"{RDF_COAR}c_93fc", "Report"),
        "REPACT": (f"{RDF_COAR}c_18gh", "Technical Report"),
        "ETABTHESE": (f"{RDF_BIBO}Document", "Document"),
        "MEMLIC": (f"{RDF_BIBO}Document", "Document"),
        "REPORT_RFOINT": (f"{RDF_BIBO}Document", "Document"),
        "REPORT_GMAST": (f"{RDF_COAR}c_93fc", "Report"),
        "REPORT_COOR": (f"{RDF_COAR}c_93fc", "Report"),
        "REPORT_RETABINT": (f"{RDF_COAR}c_93fc", "Report"),
    }

    UKNOWN_CODE = ("Unknown", "Unknown")

    @staticmethod
    def convert(code: str) -> tuple[str, str]:
        """
        Given a HAL document type code, return the corresponding uri and label
        """
        if code not in HalDocumentTypeConverter.CODES_MAPPING:
            logger.warning(
                f"Unknown HAL document type code: {code}",
            )
            return HalDocumentTypeConverter.UKNOWN_CODE

        return HalDocumentTypeConverter.CODES_MAPPING[code]
