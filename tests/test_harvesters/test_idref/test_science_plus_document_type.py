from app.harvesters.idref.science_plus_document_type_converter import (
    SciencePlusDocumentTypeConverter,
)


def test_known_science_plus_document_type():
    """
    GIVEN a known Science+ document type
    WHEN the document type converter is called
    THEN the document type is converted into the corresponding uri and label
    """
    document_type = "http://purl.org/ontology/bibo/Article"
    convert = SciencePlusDocumentTypeConverter().convert(document_type)
    assert convert == ("http://purl.org/ontology/bibo/Article", "Article")


def test_unknown_science_plus_document_type(caplog):
    """
    GIVEN an unknown Science+ document type
    WHEN the document type converter is called
    THEN the Unknown document type is returned
    """
    document_type = "UNKNOWN"
    convert = SciencePlusDocumentTypeConverter().convert(document_type)
    assert convert == ("http://data.crisalid.org/ref/document_types/unknown", "Unknown")
    assert f"Unknown SciencePlus document type: {document_type}" in caplog.text
