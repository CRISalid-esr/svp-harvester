import pytest

from app.harvesters.json_harvester_raw_result import JsonHarvesterRawResult
from app.harvesters.scanr.scanr_references_converter import ScanrReferencesConverter


@pytest.fixture(name="scanr_api_publication_cleaned_response")
def fixture_scanr_api_publication_cleaned_response(scanr_api_docs_from_publication):
    """Return the list of dictionaries references from scanr response"""
    return scanr_api_docs_from_publication["hits"]["hits"]


@pytest.fixture(name="scanr_api_publication_with_dupe_cleaned_response")
def fixture_scanr_api_publication_with_dupe_cleaned_response(
    scanr_api_docs_from_publication_with_default_dupe,
):
    """Return the list of dictionaries references from scanr response"""
    return scanr_api_docs_from_publication_with_default_dupe["hits"]["hits"]


@pytest.fixture(name="scanr_api_publication_for_author_dupe_cleaned_response")
def fixture_scanr_api_publication_with_author_dupe_cleaned_response(
    scanr_api_docs_from_publication_for_authors_dupe,
):
    """Return the list of dictionaries references from scanr response"""
    return scanr_api_docs_from_publication_for_authors_dupe["hits"]["hits"]


async def test_convert(scanr_api_publication_cleaned_response):
    """
    Test that the converter will return normalised references
    including None languages if the value is not identical to other elements with set language
    """
    converter_under_tests = ScanrReferencesConverter()

    expected_identifier = "nnt2019lysem032"
    expected_titles = {
        None: "Sécurité adaptative et énergétiquement efficace dans l’Internet des Objets"
    }
    expected_abstracts = {
        None: "La sécurité des circuits intégrés pour l’IoT "
        "est généralement incompatible avec[...]",
        "fr": "La sécurité des circuits intégrés pour l’IoT "
        "est généralement incompatible avec la [...]",
        "en": "The goal of this work is to propose new methods that provide both a high security"
        " and a high energy efficiency[...]",
    }

    for doc in scanr_api_publication_cleaned_response:
        result = JsonHarvesterRawResult(
            source_identifier=doc.get("_id"), payload=doc, formatter_name="SCANR"
        )

        test_reference = await converter_under_tests.convert(result)

        test_titles = {title.language: title.value for title in test_reference.titles}
        test_abstracts = {
            abstract.language: abstract.value for abstract in test_reference.abstracts
        }

        assert test_reference.source_identifier == expected_identifier
        assert test_titles == expected_titles
        assert test_abstracts == expected_abstracts


async def test_convert_with_default_dupe(
    scanr_api_publication_with_dupe_cleaned_response,
):
    """
    Test that the converter will return normalised references without default language
    if it's value is the same as an existing element with a set language
    """
    converter_under_tests = ScanrReferencesConverter()

    expected_identifier = "nnt2019lysem032"
    expected_titles = {
        "fr": "Sécurité adaptative et énergétiquement efficace dans l’Internet des Objets"
    }
    expected_abstracts = {
        "fr": "La sécurité des circuits intégrés pour l’IoT est"
        " généralement incompatible avec la [...]",
        "en": "The goal of this work is to propose new methods that provide both a high security"
        " and a high energy efficiency[...]",
    }

    for doc in scanr_api_publication_with_dupe_cleaned_response:
        result = JsonHarvesterRawResult(
            source_identifier=doc.get("_id"), payload=doc, formatter_name="SCANR"
        )

        test_reference = await converter_under_tests.convert(result)

        test_titles = {title.language: title.value for title in test_reference.titles}
        test_abstracts = {
            abstract.language: abstract.value for abstract in test_reference.abstracts
        }

        assert test_reference.source_identifier == expected_identifier
        assert test_titles == expected_titles
        assert test_abstracts == expected_abstracts


async def test_same_contributor_with_different_roles(
    scanr_api_publication_for_author_dupe_cleaned_response,
):
    """
    Test that the converter will return contributors with multiple roles
    """

    converter_under_tests = ScanrReferencesConverter()

    for doc in scanr_api_publication_for_author_dupe_cleaned_response:
        result = JsonHarvesterRawResult(
            source_identifier=doc.get("_id"), payload=doc, formatter_name="SCANR"
        )

        test_reference = await converter_under_tests.convert(result)
        # Create a dictionary to count the occurrences of each contributor source_identifier
        contributor_roles = {}

        # Iterate over the contributions
        for contribution in test_reference.contributions:
            # Get the contributor source_identifier and role
            contributor_source_identifier = contribution.contributor.source_identifier
            role = contribution.role

            # If the contributor source_identifier is not in the dictionary, add it with a set containing the role
            if contributor_source_identifier not in contributor_roles:
                contributor_roles[contributor_source_identifier] = {role}
            # If the contributor source_identifier is already in the dictionary, add the role to the set
            else:
                contributor_roles[contributor_source_identifier].add(role)

        # Assert that the number of roles for the contributor source_identifier of interest is equal to the expected number of roles
        assert len(contributor_roles["idref122796527"]) == 2
        assert len(contributor_roles["idref034869417"]) == 2
        assert len(contributor_roles["idref132138123"]) == 2
        assert len(contributor_roles["idref135685141"]) == 2
        assert len(contributor_roles["idref243745753"]) == 1
        assert len(contributor_roles["idref061235563"]) == 1
        assert len(contributor_roles["idref034105700"]) == 1
        # Check that the returned Reference object has the correct properties
        assert len(test_reference.contributions) == 11
