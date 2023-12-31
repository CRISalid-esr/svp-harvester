import pytest

from app.harvesters.idref.science_plus_references_converter import (
    SciencePlusReferencesConverter,
)


@pytest.mark.asyncio
async def test_science_plus_convert_for_rdf_result(
    science_plus_rdf_result_for_doc,
):
    """
    GIVEN a SciencePlusReferencesConverter instance and a sudoc RDF result for a document
    WHEN the convert method is called
    THEN it should return a Reference instance with the expected values

    :param science_plus_rdf_result_for_doc: a science plus RDF result for a document
    :return: None
    """
    converter_under_tests = SciencePlusReferencesConverter()
    expected_french_title = (
        "Marges urbaines, marges rurales entre Santiago du Chili et Valparaíso"
    )
    expected_french_abstract_beginning = (
        "La Cordillère de la Côte, "
        "entre Santiago du Chili et Valparaíso a vu son accessibilité "
    )
    result = await converter_under_tests.convert(science_plus_rdf_result_for_doc)
    assert result.source_identifier == str(
        science_plus_rdf_result_for_doc.source_identifier
    )
    # assert that there are two titles
    assert len(result.titles) == 2
    # assert that the expected french title is one of the titles at any position
    assert expected_french_title in [title.value for title in result.titles]
    # expect that one of the abstacts begins with the expected french abstract beginning
    assert any(
        abstract.value.startswith(expected_french_abstract_beginning)
        for abstract in result.abstracts
    )
