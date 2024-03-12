from app.harvesters.open_alex.open_alex_document_type_converter import (
    OpenAlexDocumentTypeConverter,
)


def test_known_open_alex_document_type():
    """
    GIVEN a known Open Alex document type
    WHEN the document type converter is called
    THEN the document type is converted into the corresponding uri and label
    """
    document_type = "article"
    convert = OpenAlexDocumentTypeConverter().convert(document_type)
    assert convert == ("http://purl.org/ontology/bibo/Article", "Article")


def test_unknown_open_alex_document_type(caplog):
    """
    GIVEN an unknown Open Alex document type
    WHEN the document type converter is called
    THEN the Unknown document type is returned
    """
    document_type = "UNKNOWN"
    convert = OpenAlexDocumentTypeConverter().convert(document_type)
    assert convert == ("http://data.crisalid.org/ref/document_types/unknown", "Unknown")
    assert f"Unknown OPEN_ALEX document type: {document_type}" in caplog.text
