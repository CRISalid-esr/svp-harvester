from app.harvesters.idref.idref_document_type_converter import (
    IdrefDocumentTypeConverter,
)


def test_known_idref_document_type():
    """
    GIVEN a known IdRef document type
    WHEN the document type converter is called
    THEN the document type is converted into the corresponding uri and label
    """
    document_type = "http://purl.org/vocab/frbr/core#Work"
    convert = IdrefDocumentTypeConverter().convert(document_type)
    assert convert == ("http://purl.org/vocab/frbr/core#Work", "Work")


def test_unknown_idref_document_type(caplog):
    """
    GIVEN an unknown IdRef document type
    WHEN the document type converter is called
    THEN the Unknown document type is returned
    """
    document_type = "UNKNOWN"
    convert = IdrefDocumentTypeConverter().convert(document_type)
    assert convert == ("http://data.crisalid.org/ref/document_types/unknown", "Unknown")
    assert f"Unknown IDREF document type: {document_type}" in caplog.text
