import pytest
from app.harvesters.exceptions.unexpected_format_exception import (
    UnexpectedFormatException,
)
from app.harvesters.idref.science_plus_references_converter import (
    SciencePlusReferencesConverter,
)


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
    expected_volume = "12"
    expected_issue = "1"
    expected_journal_title = "Cellular and Molecular Neurobiology"

    test_reference = converter_under_tests.build(
        raw_data=science_plus_rdf_result_for_doc
    )
    assert test_reference.source_identifier == str(
        science_plus_rdf_result_for_doc.source_identifier
    )
    await converter_under_tests.convert(
        raw_data=science_plus_rdf_result_for_doc, new_ref=test_reference
    )

    # assert that there are two titles
    assert len(test_reference.titles) == 2
    # assert that the expected french title is one of the titles at any position
    assert expected_french_title in [title.value for title in test_reference.titles]
    # expect that one of the abstacts begins with the expected french abstract beginning
    assert any(
        abstract.value.startswith(expected_french_abstract_beginning)
        for abstract in test_reference.abstracts
    )
    assert test_reference.issue.volume == expected_volume
    assert test_reference.issue.number == expected_issue
    assert expected_journal_title in test_reference.issue.journal.titles


async def test_science_plus_convert_for_rdf_without_title(
    science_plus_rdf_result_without_title,
):
    """
    GIVEN a SciencePlusReferencesConverter instance and a sudoc RDF result for a document
    WHEN the convert method is called
    THEN it should return a Reference instance with the expected values

    :param science_plus_rdf_result_for_doc: a science plus RDF result for a document
    :return: None
    """
    converter_under_tests = SciencePlusReferencesConverter()

    test_reference = converter_under_tests.build(
        raw_data=science_plus_rdf_result_without_title
    )

    with pytest.raises(UnexpectedFormatException) as exc_info:
        await converter_under_tests.convert(
            raw_data=science_plus_rdf_result_without_title, new_ref=test_reference
        )

    assert exc_info.match("titles should be set on reference")
