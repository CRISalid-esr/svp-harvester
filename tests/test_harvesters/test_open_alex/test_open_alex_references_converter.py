import pytest
from app.harvesters.json_harvester_raw_result import JsonHarvesterRawResult

from app.harvesters.open_alex.open_alex_references_converter import (
    OpenAlexReferencesConverter,
)


@pytest.mark.asyncio
async def test_convert(open_alex_api_work: dict):
    """Test that the converter will return normalised references"""
    converter_under_tests = OpenAlexReferencesConverter()

    expected_title = "Development of the Colle-Salvetti correlation-energy formula into a functional of the electron density"
    expected_abstract = (
        "insertion gradient expansions for density, density-functional formulas"
    )
    expected_document_type = "Article"
    expected_subjects = ["Test concept", "Concept de test", "Concepto de test"]
    expected_id = "https://openalex.org/W2023271753"
    expected_source_contributor = "open_alex"
    expected_contributors_name = ["Chengteh Lee", "Weitao Yang", "Robert G. Parr"]

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

    test_reference = await converter_under_tests.convert(result)

    assert test_reference.titles[0].value == expected_title
    assert expected_abstract in test_reference.abstracts[0].value
    assert test_reference.document_type[0].label == expected_document_type
    for concept in test_reference.subjects:
        for label in concept.labels:
            assert label.value in expected_subjects
    assert len(test_reference.subjects) == 1
    assert test_reference.source_identifier == expected_id
    assert len(test_reference.contributions) == len(expected_contributors_name)
    for contribution in test_reference.contributions:
        assert contribution.contributor.name in expected_contributors_name
        assert contribution.contributor.source == expected_source_contributor
    assert any(
        identifier.value in expected_reference_identifier
        for identifier in test_reference.identifiers
    )
    assert all(
        identifier.type not in expected_reference_identifier_ignored
        for identifier in test_reference.identifiers
    )
