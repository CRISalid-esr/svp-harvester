import datetime

import pytest
from semver import VersionInfo

from app.harvesters.exceptions.unexpected_format_exception import (
    UnexpectedFormatException,
)
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
    expected_created_date = datetime.date(2016, 6, 13)

    test_reference = converter_under_tests.build(
        raw_data=sudoc_rdf_result_for_doc, harvester_version=VersionInfo.parse("0.0.0")
    )
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
    assert test_reference.issue.journal.issn_l == expected_issn_l
    assert test_reference.created == expected_created_date


@pytest.mark.asyncio
async def test_convert_for_rdf_result_without_title(
    sudoc_rdf_result_for_doc_without_title,
):
    """
    GIVEN a SudocReferencesConverter instance and a Sudoc RDF result
    WHEN the convert method is called
    THEN it should return a Reference instance with the expected values

    :param sudoc_rdf_result_for_doc: sudoc RDF result for a document
    :return: None
    """
    converter_under_tests = SudocReferencesConverter()

    test_reference = converter_under_tests.build(
        raw_data=sudoc_rdf_result_for_doc_without_title,
        harvester_version=VersionInfo.parse("0.0.0"),
    )
    assert test_reference.source_identifier == str(
        sudoc_rdf_result_for_doc_without_title.source_identifier
    )

    with pytest.raises(UnexpectedFormatException) as exc_info:
        await converter_under_tests.convert(
            raw_data=sudoc_rdf_result_for_doc_without_title, new_ref=test_reference
        )

    assert exc_info.match("Sudoc reference without title:")


@pytest.mark.asyncio
async def test_convert_for_rdf_result_for_book(sudoc_rdf_result_for_book):
    """
    GIVEN a SudocReferencesConverter instance and a Sudoc RDF result
    WHEN the convert method is called
    THEN it should return a Reference instance with the expected Book values
    """
    converter_under_tests = SudocReferencesConverter()

    test_reference = converter_under_tests.build(
        raw_data=sudoc_rdf_result_for_book, harvester_version=VersionInfo.parse("0.0.0")
    )
    await converter_under_tests.convert(
        raw_data=sudoc_rdf_result_for_book, new_ref=test_reference
    )

    expected_publisher = "Cambridge, MA : Academic Press, an imprint of Elsevier , 2020"
    expected_isbn10 = "0128186755"
    expected_isbn13 = "9780128186756"
    expected_title = "Tumor immunology and immunotherapy Part B, : cellular methods / edited by Lorenzo Galluzzi,... Nils-Petter Rudqvist,..."

    assert expected_isbn10 == test_reference.book.isbn10
    assert expected_isbn13 == test_reference.book.isbn13
    assert expected_publisher == test_reference.book.publisher
    assert expected_title in test_reference.book.title
