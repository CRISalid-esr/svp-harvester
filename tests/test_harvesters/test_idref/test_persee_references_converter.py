import pytest

from app.harvesters.idref.persee_references_converter import PerseeReferencesConverter


@pytest.mark.asyncio
@pytest.mark.current
async def test_persee_convert_for_rdf_result(persee_rdf_result_for_doc):
    """
    GIVEN a PerseeReferencesConverter instance and a Persee RDF result for a document
    WHEN the convert method is called
    THEN it should return a Reference instance with the expected values

    :param: a Persee RDF result for a document
    :return: None
    """
    converter_under_tests = PerseeReferencesConverter()

    expected_source_identifier = (
        "http://data.persee.fr/doc/hista_0992-2059_1998_num_42_1_2826#Web"
    )
    expected_abstract_en = "designed for university education buildings dates back to the end of the 18th century, but the golden"
    expected_abstract_language = "en"
    expected_title = "Le décor peint des établissements d’enseignement supérieur à Paris. De la conception à la réception"
    expected_document_type = "Document"
    expected_auth_name = "Christian Hottin"

    test_reference = converter_under_tests.build(raw_data=persee_rdf_result_for_doc)
    assert test_reference.source_identifier == expected_source_identifier
    await converter_under_tests.convert(
        raw_data=persee_rdf_result_for_doc, new_ref=test_reference
    )
    assert expected_title == test_reference.titles[0].value
    assert expected_abstract_en in test_reference.abstracts[0].value
    assert expected_abstract_language == test_reference.abstracts[0].language
    assert any(
        document_type.label == expected_document_type
        for document_type in test_reference.document_type
    )
    assert len(test_reference.contributions) == 1
    assert expected_auth_name == test_reference.contributions[0].contributor.name.value
    assert test_reference.identifiers[0].value == expected_source_identifier
