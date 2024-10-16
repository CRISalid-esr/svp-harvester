import pytest
from semver import VersionInfo

from app.harvesters.json_harvester_raw_result import JsonHarvesterRawResult
from app.harvesters.scanr.scanr_references_converter import ScanrReferencesConverter


@pytest.fixture(name="scanr_publication_doc_with_keywords_domains")
def fixture_scanr_api_publication_cleaned_response(
    scanr_publication_doc_with_keywords_domains,
):
    """Return the list of dictionaries references from scanr response"""
    return scanr_publication_doc_with_keywords_domains["hits"]["hits"]


@pytest.fixture(name="scanr_publication_doc_with_identical_keywords_domains")
def fixture_scanr_api_publication_cleaned_dupe_keywords_response(
    scanr_publication_doc_with_identical_keywords_domains,
):
    """Return the list of dictionaries references from scanr response"""
    return scanr_publication_doc_with_identical_keywords_domains["hits"]["hits"]


@pytest.fixture(name="scanr_publication_doc_with_identical_sudoc_and_keywords_domains")
def fixture_scanr_api_publication_cleaned_dupe_sudoc_and_keywords_response(
    scanr_publication_doc_with_identical_sudoc_and_keywords_domains,
):
    """Return the list of dictionaries references from scanr response"""
    return scanr_publication_doc_with_identical_sudoc_and_keywords_domains["hits"][
        "hits"
    ]


@pytest.fixture(name="scanr_publication_doc_with_sudoc_domains")
def fixture_scanr_publication_doc_with_sudoc_domains(
    scanr_publication_doc_with_sudoc_domains,
):
    """Return the list of dictionaries references from scanr response"""
    return scanr_publication_doc_with_sudoc_domains["hits"]["hits"]


@pytest.fixture(name="scanr_publication_doc_with_wikidata_domains")
def fixture_scanr_publication_doc_with_wikidata_domains(
    scanr_publication_doc_with_wikidata_domains,
):
    """Return the list of dictionaries references from scanr response"""
    return scanr_publication_doc_with_wikidata_domains["hits"]["hits"]


async def test_convert_publication_with_keywords(
    scanr_publication_doc_with_keywords_domains,
):
    converter_under_tests = ScanrReferencesConverter()

    expected_subjects = [(None, "Efficacité énergétique")]

    for doc in scanr_publication_doc_with_keywords_domains:
        result = JsonHarvesterRawResult(
            source_identifier=doc.get("_id"), payload=doc, formatter_name="SCANR"
        )

        test_reference = converter_under_tests.build(
            raw_data=result, harvester_version=VersionInfo.parse("0.0.0")
        )
        await converter_under_tests.convert(raw_data=result, new_ref=test_reference)

        test_subjects = [
            (label.language, label.value)
            for concept in test_reference.subjects
            for label in concept.labels
        ]
        assert test_subjects == expected_subjects


async def test_convert_publication_with_identical_keywords(
    scanr_publication_doc_with_identical_keywords_domains,
):
    """
    GIVEN a publication with free keywords very similar to wikidata keywords
    WHEN the publication is converted
    THEN the very similar free keywords are eliminated
    and only the wikidata keywords are kept
    :param scanr_publication_doc_with_identical_keywords_domains:
    :return:
    """
    converter_under_tests = ScanrReferencesConverter()

    expected_subjects = [
        ("en", "Test concept"),
        ("fr", "Concept de test"),
        ("es", "Concepto de test"),
        (None, "Efficacité énergétique"),
    ]

    for doc in scanr_publication_doc_with_identical_keywords_domains:
        result = JsonHarvesterRawResult(
            source_identifier=doc.get("_id"), payload=doc, formatter_name="SCANR"
        )

        test_reference = converter_under_tests.build(
            raw_data=result, harvester_version=VersionInfo.parse("0.0.0")
        )
        await converter_under_tests.convert(raw_data=result, new_ref=test_reference)

        test_subjects = [
            (label.language, label.value)
            for concept in test_reference.subjects
            for label in concept.labels
        ]
        assert test_subjects == expected_subjects


async def test_convert_publication_with_sudoc(
    scanr_publication_doc_with_sudoc_domains,
):
    converter_under_tests = ScanrReferencesConverter()

    expected_subjects = [(None, "Internet des objets")]

    for doc in scanr_publication_doc_with_sudoc_domains:
        result = JsonHarvesterRawResult(
            source_identifier=doc.get("_id"), payload=doc, formatter_name="SCANR"
        )

        test_reference = converter_under_tests.build(
            raw_data=result, harvester_version=VersionInfo.parse("0.0.0")
        )
        await converter_under_tests.convert(raw_data=result, new_ref=test_reference)

        test_subjects = [
            (label.language, label.value)
            for concept in test_reference.subjects
            for label in concept.labels
        ]
        assert test_subjects == expected_subjects


async def test_convert_publication_with_identical_sudoc_andkeywords(
    scanr_publication_doc_with_identical_sudoc_and_keywords_domains,
):
    converter_under_tests = ScanrReferencesConverter()

    expected_subjects = [("fr", "Efficacité énergétique")]

    for doc in scanr_publication_doc_with_identical_sudoc_and_keywords_domains:
        result = JsonHarvesterRawResult(
            source_identifier=doc.get("_id"), payload=doc, formatter_name="SCANR"
        )

        test_reference = converter_under_tests.build(
            raw_data=result, harvester_version=VersionInfo.parse("0.0.0")
        )
        await converter_under_tests.convert(raw_data=result, new_ref=test_reference)

        test_subjects = [
            (label.language, label.value)
            for concept in test_reference.subjects
            for label in concept.labels
        ]
        assert test_subjects == expected_subjects


async def test_convert_publication_with_wikidata(
    scanr_publication_doc_with_wikidata_domains,
):
    converter_under_tests = ScanrReferencesConverter()

    expected_subjects = [
        ("en", "Test concept"),
        ("fr", "Concept de test"),
        ("es", "Concepto de test"),
    ]

    for doc in scanr_publication_doc_with_wikidata_domains:
        result = JsonHarvesterRawResult(
            source_identifier=doc.get("_id"), payload=doc, formatter_name="SCANR"
        )

        test_reference = converter_under_tests.build(
            raw_data=result, harvester_version=VersionInfo.parse("0.0.0")
        )
        await converter_under_tests.convert(raw_data=result, new_ref=test_reference)

        test_subjects = [
            (label.language, label.value)
            for concept in test_reference.subjects
            for label in concept.labels
        ]
        assert test_subjects == expected_subjects


# TODO: Make tests who tell the expected results of the new convert method
