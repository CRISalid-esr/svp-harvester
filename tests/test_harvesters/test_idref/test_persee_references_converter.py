import pytest

from app.harvesters.idref.persee_references_converter import PerseeReferencesConverter


@pytest.mark.asyncio
async def test_parsee_convert_for_rdf_result(persee_rdf_result_for_doc):
    """
    GIVEN a PerseeReferencesConverter instance and a Persee RDF result for a document
    WHEN the convert method is called
    THEN it should return a Reference instance with the expected values

    :param: a Persee RDF result for a document
    :return: None
    """
    converter_under_tests = PerseeReferencesConverter()

    result = await converter_under_tests.convert(persee_rdf_result_for_doc)

    expected_source_identifier = (
        "http://data.persee.fr/doc/hista_0992-2059_1998_num_42_1_2826#Web"
    )
    expected_abstract_en = "designed for university education buildings dates back to the end of the 18th century, but the golden"
    expected_abstract_language = "en"

    expected_title = "Le décor peint des établissements d’enseignement supérieur à Paris. De la conception à la réception"

    expected_document_type = "Document"

    expected_auth_name = "Christian Hottin"

    assert result.source_identifier == expected_source_identifier
    assert expected_title == result.titles[0].value
    assert expected_abstract_en in result.abstracts[0].value
    assert expected_abstract_language == result.abstracts[0].language
    assert any(
        document_type.label == expected_document_type
        for document_type in result.document_type
    )
    assert len(result.contributions) == 1
    assert expected_auth_name == result.contributions[0].contributor.name.value
    assert result.identifiers[0].value == expected_source_identifier
