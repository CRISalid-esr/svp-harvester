from app.harvesters.abstract_document_type_converter import (
    AbstractDocumentTypeConverter,
)


class HalDocumentTypeConverter(AbstractDocumentTypeConverter):
    """
    Use mapping table ton convert hal document type values to loc document type values
    """

    HARVESTER = "HAL"

    RDF = AbstractDocumentTypeConverter.RDF

    TYPES_MAPPING = {
        # HAL docType_s
        "ART": (f"{RDF['BIBO']}Article", "Article"),
        "COMM": (
            f"{RDF['SPAR']}ConferencePaper",
            "Conference Paper",
        ),
        "COUV": (f"{RDF['BIBO']}Chapter", "Chapter"),
        "THESE": (f"{RDF['BIBO']}Thesis", "Thesis"),
        "OUV": (f"{RDF['BIBO']}Book", "Book"),
        "UNDEFINDED": (f"{RDF['SPAR']}Preprint", "Preprint"),
        "MEM": (
            "https://vocabularies.coar-repositories.org/resource_types/c_bdcc/",
            "Master Thesis",
        ),
        "OTHER": (f"{RDF['COAR']}c_1843", "Other"),
        "REPORT": (f"{RDF['SPAR']}Report", "Report"),
        "IMG": (f"{RDF['SPAR']}Image", "Image"),
        "POSTER": (
            f"{RDF['SPAR']}ConferencePoster",
            "Conference Poster",
        ),
        "ISSUE": (f"{RDF['BIBO']}Document", "Document"),
        "NOTICE": (f"{RDF['BIBO']}Document", "Document"),
        "PROCEEDINGS": (
            f"{RDF['BIBO']}Proceedings",
            "Proceedings",
        ),
        "HDR": (f"{RDF['BIBO']}Document", "Document"),
        "BLOG": (f"{RDF['COAR']}c_6947", "Blog Post"),
        "PATENT": (f"{RDF['BIBO']}Patent", "Patent"),
        "REPORT_LABO": (f"{RDF['COAR']}c_93fc", "Report"),
        "VIDEO": (
            f"{RDF['BIBO']}AudioVisualDocument",
            "Audiovisual Document",
        ),
        "REPORT_MAST": (f"{RDF['COAR']}c_93fc", "Report"),
        "LECTURE": (f"{RDF['COAR']}c_8544", "Lecture"),
        "REPORT_LPRO": (f"{RDF['COAR']}c_93fc", "Report"),
        "REPORT_LICE": (f"{RDF['COAR']}c_93fc", "Report"),
        "TRAD": (f"{RDF['COAR']}c_1843", "Other"),
        "SOFTWARE": (f"{RDF['COAR']}c_5ce6", "Software"),
        "PRESCONF": (
            f"{RDF['COAR']}c_c94f",
            "Conference Output",
        ),
        "CREPORT": (f"{RDF['COAR']}c_93fc", "Report"),
        "REPORT_DOCT": (f"{RDF['COAR']}c_93fc", "Report"),
        "REPORT_ETAB": (f"{RDF['COAR']}c_93fc", "Report"),
        "MAP": (f"{RDF['BIBO']}Map", "Map"),
        "REPORTFORM": (f"{RDF['COAR']}c_93fc", "Report"),
        "OTHERREPORT": (f"{RDF['COAR']}c_18wq", "Report"),
        "NOTE": (f"{RDF['BIBO']}Note", "Note"),
        "SYNTHESE": (f"{RDF['BIBO']}Document", "Document"),
        "REPORT_FPROJ": (f"{RDF['COAR']}c_93fc", "Report"),
        "REPORT_GLICE": (f"{RDF['COAR']}c_93fc", "Report"),
        "REPACT": (
            f"{RDF['COAR']}c_18gh",
            "Technical Report",
        ),
        "ETABTHESE": (f"{RDF['BIBO']}Document", "Document"),
        "MEMLIC": (f"{RDF['BIBO']}Document", "Document"),
        "REPORT_RFOINT": (
            f"{RDF['BIBO']}Document",
            "Document",
        ),
        "REPORT_GMAST": (f"{RDF['COAR']}c_93fc", "Report"),
        "REPORT_COOR": (f"{RDF['COAR']}c_93fc", "Report"),
        "REPORT_RETABINT": (
            f"{RDF['COAR']}c_93fc",
            "Report",
        ),
        # HAL docSubType_s
        "PHOTOGRAPHY": (
            f"{RDF['SPAR']}StillImage",
            "Still Image",
        ),
        "RESREPORT": (
            f"{RDF['COAR']}c_18ws",
            "Research Report",
        ),
        "BOOKREVIEW": (
            f"{RDF['SPAR']}BookReview",
            "Book Review",
        ),
        "ARTREV": (
            f"{RDF['SPAR']}ReviewArticle",
            "Review Article",
        ),
        "ILLUSTRATION": (
            f"{RDF['SPAR']}StillImage",
            "Still Image",
        ),
        "TECHREPORT": (
            f"{RDF['SPAR']}TechnicalReport",
            "Technical Report",
        ),
        "GRAPHICS": (
            f"{RDF['SPAR']}StillImage",
            "Still Image",
        ),
        "WORKINGPAPER": (
            f"{RDF['SPAR']}WorkingPaper",
            "Working Paper",
        ),
        "DATAPAPER": (f"{RDF['COAR']}c_beb9", "Data Paper"),
        "FUNDREPORT": (f"{RDF['SPAR']}Report", "Report"),
        "PREPRINT": (f"{RDF['SPAR']}Preprint", "Preprint"),
        "EXPERTREPORT": (f"{RDF['SPAR']}Report", "Report"),
        "SYNTOUV": (f"{RDF['BIBO']}Book", "Book"),
        "CRIT": (f"{RDF['BIBO']}Book", "Book"),
        "MANUAL": (f"{RDF['BIBO']}Manual", "Manual"),
        "DRAWING": (
            f"{RDF['SPAR']}StillImage",
            "Still Image",
        ),
        "GRAVURE": (
            f"{RDF['SPAR']}StillImage",
            "Still Image",
        ),
        "DICTIONARY": (
            f"{RDF['SPAR']}ReferenceBook",
            "Reference Book",
        ),
        "DMP": (
            f"{RDF['SPAR']}DataMangementPlan",
            "Data Management Plan",
        ),
    }
