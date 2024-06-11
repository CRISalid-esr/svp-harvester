import datetime

import pytest
from semver import VersionInfo

from app.harvesters.json_harvester_raw_result import JsonHarvesterRawResult

from app.harvesters.open_alex.open_alex_references_converter import (
    OpenAlexReferencesConverter,
)


@pytest.mark.asyncio
async def test_convert(open_alex_api_work: dict):
    """Test that the converter will return normalised references"""
    converter_under_tests = OpenAlexReferencesConverter()

    expected_title = (
        "Development of the Colle-Salvetti "
        "correlation-energy formula into a functional of the electron density"
    )
    expected_abstract = (
        "insertion gradient expansions for density, density-functional formulas"
    )
    expected_document_type = "Article"
    expected_subjects = ["Test concept", "Concept de test", "Concepto de test"]
    expected_id = "https://openalex.org/W2023271753"
    expected_source_contributor = "open_alex"
    expected_contributors_name_rank = {
        "Chengteh Lee": 1,
        "Weitao Yang": 2,
        "Robert G. Parr": 3,
    }

    result = JsonHarvesterRawResult(
        source_identifier=open_alex_api_work["id"],
        payload=open_alex_api_work,
        formatter_name="OPEN_ALEX",
    )

    expected_reference_identifier = [
        "https://openalex.org/W2023271753",
        "https://doi.org/10.1103/physrevb.37.785",
        "https://pubmed.ncbi.nlm.nih.gov/9944570",
    ]

    expected_reference_identifier_ignored = ["mag"]

    expected_page = "785-789"
    expected_volume = "37"
    expected_issue_number = ["237"]
    expected_publisher = "American Physical Society"
    expected_issn = "2469-9896"
    expected_issued_date = datetime.date(1988, 1, 15)
    expected_created_date = datetime.date(2016, 6, 24)

    test_reference = converter_under_tests.build(
        raw_data=result, harvester_version=VersionInfo.parse("0.0.0")
    )
    await converter_under_tests.convert(raw_data=result, new_ref=test_reference)

    assert test_reference.source_identifier == expected_id
    assert test_reference.harvester == "OpenAlex"
    assert test_reference.titles[0].value == expected_title
    assert expected_abstract in test_reference.abstracts[0].value
    assert test_reference.document_type[0].label == expected_document_type
    for concept in test_reference.subjects:
        for label in concept.labels:
            assert label.value in expected_subjects
    assert len(test_reference.subjects) == 1
    assert len(test_reference.contributions) == len(expected_contributors_name_rank)
    for contribution in test_reference.contributions:
        assert contribution.contributor.name in expected_contributors_name_rank
        assert contribution.contributor.source == expected_source_contributor
        assert (
            contribution.rank
            == expected_contributors_name_rank[contribution.contributor.name]
        )
    assert any(
        identifier.value in expected_reference_identifier
        for identifier in test_reference.identifiers
    )
    assert all(
        identifier.type not in expected_reference_identifier_ignored
        for identifier in test_reference.identifiers
    )
    assert test_reference.page == expected_page
    assert test_reference.issue.volume == expected_volume
    assert test_reference.issue.number == expected_issue_number
    assert test_reference.issue.journal.publisher == expected_publisher
    assert expected_issn in test_reference.issue.journal.issn
    assert test_reference.issued == expected_issued_date
    assert test_reference.created == expected_created_date
    assert len(test_reference.manifestations) == 3
    assert (
        test_reference.manifestations[0].page
        == "https://doi.org/10.1103/physrevb.37.785"
    )
    assert test_reference.manifestations[0].download_url == None
    assert (
        test_reference.manifestations[1].page
        == "https://cdr.lib.unc.edu/downloads/p2677460w"
    )
    assert (
        test_reference.manifestations[1].download_url
        == "https://cdr.lib.unc.edu/downloads/p2677460w"
    )
    assert (
        test_reference.manifestations[2].page
        == "https://pubmed.ncbi.nlm.nih.gov/9944570"
    )
    assert test_reference.manifestations[2].download_url == None


@pytest.mark.parametrize(
    "field_tested, reference_field, tested_value, expected_log",
    [
        ("publication_date", "issued", "invalid_date", "Could not parse date"),
        ("publication_date", "issued", 123, "Date should be"),
        ("created_date", "created", "invalid_date", "Could not parse date"),
        ("created_date", "created", 123, "Date should be"),
    ],
)
async def test_convert_with_date_exception(
    open_alex_api_work: dict,
    field_tested,
    reference_field,
    tested_value,
    expected_log,
    caplog,
):
    """test that converter will raise an error when date is in invalid format"""
    converter_under_tests = OpenAlexReferencesConverter()

    open_alex_api_work[field_tested] = tested_value

    result = JsonHarvesterRawResult(
        source_identifier=open_alex_api_work["id"],
        payload=open_alex_api_work,
        formatter_name="OPEN_ALEX",
    )

    expected_id = "https://openalex.org/W2023271753"

    test_reference = converter_under_tests.build(
        raw_data=result, harvester_version=VersionInfo.parse("0.0.0")
    )
    await converter_under_tests.convert(raw_data=result, new_ref=test_reference)

    assert test_reference.source_identifier == expected_id
    assert getattr(test_reference, reference_field) is None
    assert "OpenAlex reference converter cannot create" in caplog.text
    assert expected_log in caplog.text
