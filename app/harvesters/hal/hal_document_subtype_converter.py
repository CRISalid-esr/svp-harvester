from app.harvesters.abstract_document_type_converter import (
    AbstractDocumentTypeConverter,
)


class HalDocumentSubtypeConverter(AbstractDocumentTypeConverter):
    """
    Use mapping table ton convert hal document type values to loc document type values
    """

    RDF_BIBO = "http://purl.org/ontology/bibo/"
    RDF_SPAR = "http://purl.org/spar/fabio/"
    RDF_COAR = "http://purl.org/coar/resource_type"

    HARVESTER = "HAL"

    TYPES_MAPPING = {
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
        "SYNTOUV": (f"Syntouv Uri", "Syntouv"),
        "CRIT": (f"Crit Uri", "Crit"),
        "MANUAL": (f"{RDF_BIBO}Manual", "Manual"),
        "DRAWING": (f"{RDF_SPAR}StillImage", "Still Image"),
        "GRAVURE": (f"{RDF_SPAR}StillImage", "Still Image"),
        "DICTIONARY": (f"{RDF_SPAR}ReferenceBook", "Reference Book"),
        "DMP": (f"{RDF_SPAR}DataMangementPlan", "Data Management Plan"),
        "NULL": (f"Null Uri", "Null"),
        "OUV": (f"Ouv Uri", "OUV"),
    }
