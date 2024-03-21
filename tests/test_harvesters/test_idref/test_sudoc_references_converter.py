from math import e
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

    expected_document_type = "Article"

    expected_journal_title = "Le Cabinet historique"
    expected_issn = "1954-6009"
    expected_issn_l = "1954-6009"

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
    assert expected_document_type in [test_reference.document_type[0].label]
    assert expected_journal_title in test_reference.issue.journal.titles
    assert expected_issn in test_reference.issue.journal.issn
    assert expected_issn_l == test_reference.issue.journal.issn_l
