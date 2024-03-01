from app.harvesters.abstract_document_type_converter import (
    AbstractDocumentTypeConverter,
)


class HalDocumentTypeConverter(AbstractDocumentTypeConverter):
    """
    Use mapping table ton convert hal document type values to loc document type values
    """

    RDF_BIBO = "http://purl.org/ontology/bibo/"
    RDF_SPAR = "http://purl.org/spar/fabio/"
    RDF_COAR = "http://purl.org/coar/resource_type"

    HARVESTER = "HAL"

    TYPES_MAPPING = {
        # HAL docType_s
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
        "PROCEEDINGS": (f"{RDF_BIBO}Proceedings", "Proceedings"),
        "HDR": (f"{RDF_BIBO}Document", "Document"),
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
        # HAL docSubType_s
        "PHOTOGRAPHY": (f"{RDF_SPAR}StillImage", "Still Image"),
        "RESREPORT": (f"{RDF_COAR}c_18ws", "Research Report"),
        "BOOKREVIEW": (f"{RDF_SPAR}BookReview", "Book Review"),
        "ARTREV": (f"{RDF_SPAR}ReviewArticle", "Review Article"),
        "ILLUSTRATION": (f"{RDF_SPAR}StillImage", "Still Image"),
        "TECHREPORT": (f"{RDF_SPAR}TechnicalReport", "Technical Report"),
        "GRAPHICS": (f"{RDF_SPAR}StillImage", "Still Image"),
        "WORKINGPAPER": (f"{RDF_SPAR}WorkingPaper", "Working Paper"),
        "DATAPAPER": (f"{RDF_COAR}c_beb9", "Data Paper"),
        "FUNDREPORT": (f"{RDF_SPAR}Report", "Report"),
        "PREPRINT": (f"{RDF_SPAR}Preprint", "Preprint"),
        "EXPERTREPORT": (f"{RDF_SPAR}Report", "Report"),
        "SYNTOUV": (f"{RDF_BIBO}Book", "Book"),
        "CRIT": (f"{RDF_BIBO}Book", "Book"),
        "MANUAL": (f"{RDF_BIBO}Manual", "Manual"),
        "DRAWING": (f"{RDF_SPAR}StillImage", "Still Image"),
        "GRAVURE": (f"{RDF_SPAR}StillImage", "Still Image"),
        "DICTIONARY": (f"{RDF_SPAR}ReferenceBook", "Reference Book"),
        "DMP": (f"{RDF_SPAR}DataMangementPlan", "Data Management Plan"),
    }
