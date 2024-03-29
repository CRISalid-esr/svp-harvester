import pytest

from app.harvesters.idref.open_edition_references_converter import (
    OpenEditionReferencesConverter,
)


@pytest.mark.asyncio
async def test_open_edition_convert_for_rfd_result(
    open_edition_xml_result_for_doc,
):
    """
    GIVEN a OpenEditionReferencesConverter instance and a Open Edition XML result for a document
    WHEN the convert method is called
    THEN it should return a Reference instance with the expected values

    :param: open_edition_xml_result_for_doc: a Open Edition RDF result for a document
    :return: None
    """
    converter_under_tests = OpenEditionReferencesConverter()
    test_reference = converter_under_tests.build(
        raw_data=open_edition_xml_result_for_doc
    )
    await converter_under_tests.convert(
        raw_data=open_edition_xml_result_for_doc, new_ref=test_reference
    )
    expected_french_title = "Les émeutes entre hindous et musulmans (partie 2)"
    expected_french_abstract_beginning = (
        "Si le caractère très ancien et les facteurs religieux des émeutes"
    )
    expected_reference_identifier = [
        "https://journals.openedition.org/conflits/756",
        "10.4000/conflits.756",
    ]
    expected_publisher = "L’Harmattan"
    expected_journal_title = "Cultures & conflits"
    expected_issue_rights = "https://creativecommons.org/licenses/by-nc-nd/4.0/"

    assert test_reference.source_identifier == str(
        open_edition_xml_result_for_doc.source_identifier
    )
    assert len(test_reference.titles) == 1
    assert expected_french_title in [title.value for title in test_reference.titles]
    assert any(
        abstract.value.startswith(expected_french_abstract_beginning)
        for abstract in test_reference.abstracts
    )
    assert any(
        identifier.value in expected_reference_identifier
        for identifier in test_reference.identifiers
    )
    assert test_reference.document_type[0].label == "Article"
    assert expected_publisher == test_reference.issue.journal.publisher
    assert expected_journal_title in test_reference.issue.journal.titles
    assert expected_issue_rights == test_reference.issue.rights
