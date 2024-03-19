from app.harvesters.idref.open_edition_document_type_converter import (
    OpenEditionDocumentTypeConverter,
)


def test_kwown_open_edition_document_type():
    """
    GIVEN a known OpenEdition document type
    WHEN the document type converter is called
    THEN the document type is converted into the corresponding uri and label
    """
    document_type = "article"
    convert = OpenEditionDocumentTypeConverter().convert(document_type)
    assert convert == (
        "http://purl.org/ontology/bibo/Article",
        "Article",
    )


def test_uknown_open_edition_document_type():
    """
    GIVEN an unknown OpenEdition document type
    WHEN the document type converter is called
    THEN the Unknown document type is returned
    """
    document_type = "UNKNOWN"
    convert = OpenEditionDocumentTypeConverter().convert(document_type)
    assert convert == ("http://data.crisalid.org/ref/document_types/unknown", "Unknown")
    assert f"Unknown Open Edition document type: {document_type}"
