import pytest

from app.harvesters.scanr.scanr_references_converter import ScanrReferencesConverter
from app.harvesters.json_harvester_raw_result import JsonHarvesterRawResult


@pytest.fixture(name="scanr_api_publication_cleaned_response")
def fixture_scanr_api_publication_cleaned_response(scanr_api_docs_from_publication):
    """Return the list of dictionaries references from scanr response"""
    return scanr_api_docs_from_publication["hits"]["hits"]


async def test_convert(scanr_api_publication_cleaned_response):
    """Test that the converter will return normalised references"""
    converter_under_tests = ScanrReferencesConverter()

    expected_identifier = "nnt2019lysem032"
    expected_titles = [
        "Sécurité adaptative et énergétiquement efficace dans l’Internet des Objets"
    ]
    expected_abstracts = [
        "La sécurité des circuits intégrés pour l’IoT est généralement incompatible avec[...]",
        "La sécurité des circuits intégrés pour l’IoT est généralement incompatible avec la [...]",
        "The goal of this work is to propose new methods that provide both a high security"
        " and a high energy efficiency[...]"
    ]

    for doc in scanr_api_publication_cleaned_response:
        result = JsonHarvesterRawResult(
            source_identifier=doc.get("_id"), payload=doc, formatter_name="SCANR"
        )

        test_reference = await converter_under_tests.convert(result)

        test_titles = [title.value for title in test_reference.titles]
        test_abstracts = [abstract.value for abstract in test_reference.abstracts]

        assert test_reference.source_identifier == expected_identifier
        assert test_titles == expected_titles
        assert test_abstracts == expected_abstracts
