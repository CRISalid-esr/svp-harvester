import pytest

from app.harvesters.idref.sudoc_references_converter import SudocReferencesConverter


@pytest.mark.asyncio
async def test_convert_for_rdf_result(
    sudoc_rdf_result_for_doc,
):
    """
    GIVEN a SudocReferencesConverter instance and a Sudoc RDF result
    WHEN the convert method is called
    THEN it should return a Reference instance with the expected values

    :param sudoc_rdf_result_for_doc: sudoc RDF result for a document
    :return: None
    """
    converter_under_tests = SudocReferencesConverter()
    expected_french_title = (
        "Agriculture des métropoles  : voie d'avenir ou cache-misère ?"
    )
    expected_french_abstract_beginning = (
        "Le présent dossier aborde la participation de cette agriculture urbaine "
    )
    result = await converter_under_tests.convert(sudoc_rdf_result_for_doc)
    assert result.source_identifier == str(sudoc_rdf_result_for_doc.source_identifier)
    # assert that there are two titles
    assert len(result.titles) == 2
    # assert that the expected french title is one of the titles at any position
    assert expected_french_title in [title.value for title in result.titles]
    # expect that one of the abstacts begins with the expected french abstract beginning
    assert any(
        abstract.value.startswith(expected_french_abstract_beginning)
        for abstract in result.abstracts
    )
    assert result.identifiers[0].value == sudoc_rdf_result_for_doc.source_identifier
