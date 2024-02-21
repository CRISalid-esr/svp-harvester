import pytest

from app.harvesters.hal.hal_references_converter import HalReferencesConverter
from app.harvesters.json_harvester_raw_result import JsonHarvesterRawResult


@pytest.fixture(name="hal_api_cleaned_response")
def fixture_hal_api_cleaned_response(hal_api_docs_for_researcher):
    """Return the list of dictionaries references from hal response"""
    return hal_api_docs_for_researcher["response"]["docs"]


@pytest.mark.asyncio
async def test_convert(hal_api_cleaned_response):  # pylint: disable=too-many-locals
    """Test that the converter will return normalised references"""
    converter_under_tests = HalReferencesConverter()

    expected_titles = [
        "Where does « Axial breakthrough » take place? "
        "In the past, or in present narratives of the past?"
    ]
    expected_subjects = [
        "Antiquity",
        "Historiography",
        "Greek city",
        "Vernant",
        "Narration of the past",
    ]
    expected_subtitles = ["test_placeholder_subtitle"]
    expected_docid = "1387023"
    expected_abstracts = ["This article focuses on Vernant..."]
    expected_contributors_number = 1
    expected_contributor_role = "Author"
    expected_contributor_name = "Violaine Sebillotte Cuchet"
    expected_contributor_source = "hal"
    expected_contributor_source_identifier = "10227"
    expected_references_identifier_types = ["hal", "doi"]
    expected_references_identifier_values = ["halshs-01387023", "doi/1234"]
    for doc in hal_api_cleaned_response:
        result = JsonHarvesterRawResult(
            source_identifier=doc["docid"], payload=doc, formatter_name="HAL"
        )

        test_reference = await converter_under_tests.convert(result)

        test_titles = [title.value for title in test_reference.titles]
        test_subtitles = [subtitles.value for subtitles in test_reference.subtitles]
        test_abstracts = [abstract.value for abstract in test_reference.abstracts]
        test_subjects = []
        for concept in test_reference.subjects:
            for label in concept.labels:
                test_subjects.append(label.value)

        assert test_titles == expected_titles
        assert test_subjects == expected_subjects
        assert test_subtitles == expected_subtitles
        assert test_abstracts == expected_abstracts
        assert test_reference.source_identifier == expected_docid
        assert len(test_reference.contributions) == expected_contributors_number
        assert test_reference.contributions[0].role == expected_contributor_role
        assert (
            test_reference.contributions[0].contributor.name
            == expected_contributor_name
        )
        assert (
            test_reference.contributions[0].contributor.source
            == expected_contributor_source
        )
        assert (
            test_reference.contributions[0].contributor.source_identifier
            == expected_contributor_source_identifier
        )
        for type, value in zip(
            expected_references_identifier_types, expected_references_identifier_values
        ):
            assert any(
                identifier.type == type and identifier.value == value
                for identifier in test_reference.identifiers


@pytest.mark.asyncio
async def test_convert_with_date_inconsistency(
    hal_api_docs_with_date_inconsistency, caplog
):
    """Test that the converter will raise an exception when the date is inconsistent"""
    converter_under_tests = HalReferencesConverter()
    for doc in hal_api_docs_with_date_inconsistency["response"]["docs"]:
        result = JsonHarvesterRawResult(
            source_identifier=doc["docid"], payload=doc, formatter_name="HAL"
        )
        reference = await converter_under_tests.convert(result)
        assert reference.issued is None
        assert reference.created is None
        assert "Could not parse date" in caplog.text
