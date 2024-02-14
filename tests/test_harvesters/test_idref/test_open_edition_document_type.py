from app.harvesters.idref.open_edition_document_type_converter import (
    OpenEditionDocumentTypeConverter,
)


def test_kwown_open_edition_document_type():
    # TODO WHEN Mapping Table is complete
    """
    GIVEN a known OpenEdition document type
    WHEN the document type converter is called
    THEN the document type is converted into the corresponding uri and label
    """
    document_type = "book"
    convert = OpenEditionDocumentTypeConverter.convert(type_document=document_type)


def test_uknown_open_edition_document_type(caplog):
    """
    GIVEN an unknown OpenEdition document type
    WHEN the document type converter is called
    THEN the Unknown document type is returned
    """
    document_type = "UKNOWN"
    convert = OpenEditionDocumentTypeConverter.convert(type_document=document_type)
    assert convert == ("http://data.crisalid.org/ref/document_types/unkown", "Uknown")
    assert f"Unknown Open Edition document type: {document_type}" in caplog.text
