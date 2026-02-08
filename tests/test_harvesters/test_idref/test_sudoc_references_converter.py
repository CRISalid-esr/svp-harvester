import datetime

import pytest
from semver import VersionInfo

from app.db.daos.contributor_dao import ContributorDAO
from app.db.session import async_session
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
    converter_under_tests = SudocReferencesConverter(name="sudoc")
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
    expected_raw_issued_date = "2016"
    expected_issued_date = datetime.date(2016, 1, 1)
    expected_issue_source_identifier = "http://www.sudoc.fr/013451154/id-sudoc"

    test_reference = converter_under_tests.build(
        raw_data=sudoc_rdf_result_for_doc, harvester_version=VersionInfo.parse("0.0.0")
    )
    expected_subjects = [
        "Idref concept allowed for test",
        "Concept Idref autorisé pour les tests",
        "Idref concept you can use for tests",
        "Concept Idref que vous pouvez utiliser pour les tests",
    ]

    assert test_reference.source_identifier == str(
        sudoc_rdf_result_for_doc.source_identifier
    )
    await converter_under_tests.convert(
        raw_data=sudoc_rdf_result_for_doc, new_ref=test_reference
    )
    test_subjects = []
    for concept in test_reference.subjects:
        for label in concept.labels:
            test_subjects.append(label.value)

    assert test_subjects == expected_subjects

    assert len(test_reference.titles) == 2
    assert expected_french_title in [title.value for title in test_reference.titles]
    assert any(
        abstract.value.startswith(expected_french_abstract_beginning)
        for abstract in test_reference.abstracts
    )

    assert any(
        identifier.type == "uri"
        and str(identifier.value) == str(sudoc_rdf_result_for_doc.source_identifier)
        for identifier in test_reference.identifiers
    )

    assert any(
        identifier.type == "sudoc_ppn" and identifier.value == "193726130"
        for identifier in test_reference.identifiers
    )
    assert expected_document_type in [test_reference.document_type[0].label]
    assert expected_journal_title in test_reference.issue.journal.titles
    assert expected_issn in test_reference.issue.journal.issn
    assert test_reference.issue.journal.issn_l == expected_issn_l
    assert test_reference.created == expected_created_date
    assert test_reference.raw_issued == expected_raw_issued_date
    assert test_reference.issued == expected_issued_date
    assert test_reference.issue.source_identifier == expected_issue_source_identifier
    assert (
        test_reference.issue.journal.source_identifier
        in test_reference.issue.source_identifier
    )
    assert len(test_reference.contributions) == 2
    contributors = []
    for contribution in test_reference.contributions:
        async with async_session() as session:
            async with session.begin_nested():
                contributor = await ContributorDAO(session).get_by_id(
                    contribution.contributor.id
                )
                contributors.append(contributor)
    contributor_1 = [
        contributor
        for contributor in contributors
        if contributor.name == "Faliès, Cécile (1982-....)"
    ][0]
    assert contributor_1.source == "sudoc"
    assert contributor_1.source_identifier == "http://www.idref.fr/193726831/id"
    assert contributor_1.identifiers[0].source == "sudoc"
    assert contributor_1.identifiers[0].type == "idref"
    assert contributor_1.identifiers[0].value == "193726831"
    contributor_2 = [
        contributor
        for contributor in contributors
        if contributor.name == "Mesclier, Évelyne (1964-....)"
    ][0]
    assert contributor_2.source == "sudoc"
    assert contributor_2.source_identifier == "http://www.idref.fr/057549222/id"
    assert contributor_2.identifiers[0].source == "sudoc"
    assert contributor_2.identifiers[0].type == "idref"
    assert contributor_2.identifiers[0].value == "057549222"


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
    converter_under_tests = SudocReferencesConverter(name="sudoc")

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
    converter_under_tests = SudocReferencesConverter(name="sudoc")

    test_reference = converter_under_tests.build(
        raw_data=sudoc_rdf_result_for_book, harvester_version=VersionInfo.parse("0.0.0")
    )
    await converter_under_tests.convert(
        raw_data=sudoc_rdf_result_for_book, new_ref=test_reference
    )

    expected_publisher = "Cambridge, MA : Academic Press, an imprint of Elsevier , 2020"
    expected_isbn10 = "0128186755"
    expected_isbn13 = "9780128186756"
    expected_title = (
        "Tumor immunology and immunotherapy Part B, :"
        " cellular methods / edited by Lorenzo Galluzzi,... Nils-Petter Rudqvist,..."
    )

    assert expected_isbn10 == test_reference.book.isbn10
    assert expected_isbn13 == test_reference.book.isbn13
    assert expected_publisher == test_reference.book.publisher
    assert expected_title in test_reference.book.title


async def test_convert_with_invalid_date_format(
    sudoc_rdf_result_for_doc_with_invalid_created, caplog
):
    """
    GIVEN a SudocReferencesConverter instance and a Sudoc RDF result with an invalid date format
    WHEN the convert method is called
    THEN it should raise a log error and the created date should be None
    """
    converter_under_tests = SudocReferencesConverter(name="sudoc")

    test_reference = converter_under_tests.build(
        raw_data=sudoc_rdf_result_for_doc_with_invalid_created,
        harvester_version=VersionInfo.parse("0.0.0"),
    )

    await converter_under_tests.convert(
        raw_data=sudoc_rdf_result_for_doc_with_invalid_created, new_ref=test_reference
    )

    assert test_reference.created is None
    assert "Sudoc reference converter cannot create" in caplog.text
    assert "Not a valid ISO-8601 datetime" in caplog.text


async def test_convert_with_empty_issued_date(
    sudoc_rdf_result_for_doc_with_empty_issued,
):
    """
    GIVEN a SudocReferencesConverter instance and a Sudoc RDF result with an empty issued date
    WHEN the convert method is called
    THEN it should return a Reference instance with the expected values
    """
    converter_under_tests = SudocReferencesConverter(name="sudoc")

    test_reference = converter_under_tests.build(
        raw_data=sudoc_rdf_result_for_doc_with_empty_issued,
        harvester_version=VersionInfo.parse("0.0.0"),
    )

    await converter_under_tests.convert(
        raw_data=sudoc_rdf_result_for_doc_with_empty_issued, new_ref=test_reference
    )

    assert test_reference.issued is None


async def test_convert_with_multiple_issued_date(
    sudoc_rdf_result_for_doc_with_multiple_issued,
):
    """
    GIVEN a SudocReferencesConverter instance and a Sudoc RDF result with multiple issued date
    WHEN the convert method is called
    THEN it should return a Reference instance with the last issued date
    """
    converter_under_tests = SudocReferencesConverter(name="sudoc")

    test_reference = converter_under_tests.build(
        raw_data=sudoc_rdf_result_for_doc_with_multiple_issued,
        harvester_version=VersionInfo.parse("0.0.0"),
    )

    await converter_under_tests.convert(
        raw_data=sudoc_rdf_result_for_doc_with_multiple_issued, new_ref=test_reference
    )

    assert test_reference.issued == datetime.date(2006, 1, 1)


async def test_convert_thesis_with(sudoc_rdf_result_for_thesis):
    """
    GIVEN a SudocReferencesConverter instance and a Sudoc RDF result for a thesis
    WHEN the convert method is called
    THEN it should return a Reference instance with theses.fr URI and NNT

    :param sudoc_rdf_result_for_thesis:
    :return:
    """
    converter_under_tests = SudocReferencesConverter(name="sudoc")
    test_reference = converter_under_tests.build(
        raw_data=sudoc_rdf_result_for_thesis,
        harvester_version=VersionInfo.parse("0.0.0"),
    )
    await converter_under_tests.convert(
        raw_data=sudoc_rdf_result_for_thesis, new_ref=test_reference
    )
    assert test_reference.source_identifier == str(
        sudoc_rdf_result_for_thesis.source_identifier
    )
    assert any(
        manifestation.page == "http://www.sudoc.fr/253147565"
        for manifestation in test_reference.manifestations
    )
    assert any(
        manifestation.page == "http://www.theses.fr/2020UPAST005/abes"
        for manifestation in test_reference.manifestations
    )
    assert any(
        manifestation.page == "https://pastel.hal.science/tel-03129996"
        for manifestation in test_reference.manifestations
    )
    # there should be an identifier of type nnt with value 2020UPAST005
    assert any(
        identifier.type == "nnt" and identifier.value == "2020UPAST005"
        for identifier in test_reference.identifiers
    )


@pytest.mark.asyncio
async def test_convert_thesis_extracts_nnt_from_rdam_p30135_when_no_bibo_uri_thesesfr(
    sudoc_rdf_result_for_thesis_without_bibo_uri_thesesfr,
):
    """
    GIVEN a thesis RDF where theses.fr URLs are not present in bibo:uri
          but are present via rdam:P30135
    WHEN convert is called
    THEN it should still add the theses.fr manifestation and extract NNT
    """
    converter_under_tests = SudocReferencesConverter(name="sudoc")
    test_reference = converter_under_tests.build(
        raw_data=sudoc_rdf_result_for_thesis_without_bibo_uri_thesesfr,
        harvester_version=VersionInfo.parse("0.0.0"),
    )

    await converter_under_tests.convert(
        raw_data=sudoc_rdf_result_for_thesis_without_bibo_uri_thesesfr,
        new_ref=test_reference,
    )

    # manifestation should have been added from rdam:P30135 ("/id" form)
    assert any(
        m.page == "http://www.theses.fr/2020UPAST005/id"
        for m in test_reference.manifestations
    )

    # NNT must be extracted even without theses.fr in bibo:uri
    assert any(
        i.type == "nnt" and i.value == "2020UPAST005"
        for i in test_reference.identifiers
    )

    # and also ensure the theses.fr /abes is NOT present (proves we're not relying on bibo:uri)
    assert not any(
        m.page == "http://www.theses.fr/2020UPAST005/abes"
        for m in test_reference.manifestations
    )
