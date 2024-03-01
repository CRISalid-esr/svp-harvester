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
    test_reference = converter_under_tests.build(raw_data=sudoc_rdf_result_for_doc)
    assert test_reference.source_identifier == str(
        sudoc_rdf_result_for_doc.source_identifier
    )
    await converter_under_tests.convert(
        raw_data=sudoc_rdf_result_for_doc, new_ref=test_reference
    )
    assert len(test_reference.titles) == 2
    assert expected_french_title in [title.value for title in test_reference.titles]
    assert any(
        abstract.value.startswith(expected_french_abstract_beginning)
        for abstract in test_reference.abstracts
    )
    assert (
        test_reference.identifiers[0].value
        == sudoc_rdf_result_for_doc.source_identifier
    )
