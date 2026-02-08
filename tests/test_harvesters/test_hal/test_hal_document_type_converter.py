from app.harvesters.hal.hal_document_type_converter import HalDocumentTypeConverter


def test_known_hal_document_type():
    """
    GIVEN a known HAL document type
    WHEN the document type converter is called
    THEN the document type is converted into the corresponding uri and label
    """
    document_type = "COMM"
    convert = HalDocumentTypeConverter().convert(document_type)
    assert convert == ("http://purl.org/spar/fabio/ConferencePaper", "Conference Paper")


def test_uknown_hal_document_type(caplog):
    """
    GIVEN an unknown HAL document type
    WHEN the document type converter is called
    THEN the Unknown document type is returned
    """
    document_type = "UKNOWN"
    convert = HalDocumentTypeConverter().convert(document_type)
    assert convert == ("http://data.crisalid.org/ref/document_types/unknown", "Unknown")
    assert f"Unknown HAL document type: {document_type}" in caplog.text
