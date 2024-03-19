from app.harvesters.scanr.scanr_document_type_converter import (
    ScanrDocumentTypeConverter,
)


def test_known_scanr_document_type():
    """
    GIVEN a known scanr document type code
    WHEN the code is converted
    THEN the corresponding uri and label are returned
    """
    document_type = "book-chapter"
    convert = ScanrDocumentTypeConverter().convert(document_type)
    assert convert == (
        "http://purl.org/ontology/bibo/Chapter",
        "Chapter",
    )


def test_unknown_scanr_document_type():
    """
    GIVEN an unknown scanr document type code
    WHEN the code is converted
    THEN the corresponding uri and label are returned
    """
    document_type = "unknown"
    convert = ScanrDocumentTypeConverter().convert(document_type)
    assert convert == (
        "http://data.crisalid.org/ref/document_types/unknown",
        "Unknown",
    )
