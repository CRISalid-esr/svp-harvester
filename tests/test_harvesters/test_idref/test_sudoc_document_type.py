from app.harvesters.idref.sudoc_document_type_converter import (
    SudocDocumentTypeConverter,
)


def test_known_sudoc_document_type():
    """
    GIVEN a known Sudoc document type
    WHEN the document type converter is called
    THEN the document type is converted into the corresponding uri and label
    """
    document_type = "Text"
    convert = SudocDocumentTypeConverter().convert(document_type)
    assert convert == ("URI", "LABEL")


def test_unknown_sudoc_document_type(caplog):
    """
    GIVEN an unknown Sudoc document type
    WHEN the document type converter is called
    THEN the Unknown document type is returned
    """
    document_type = "UNKNOWN"
    convert = SudocDocumentTypeConverter().convert(document_type)
    assert convert == ("http://data.crisalid.org/ref/document_types/unknown", "Unknown")
    assert f"Unknown Sudoc document type: {document_type}" in caplog.text
