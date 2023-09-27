import pytest

from app.harvesters.hal.hal_references_converter import HalReferencesConverter


@pytest.fixture(name="hal_api_cleaned_response")
def fixture_hal_api_cleaned_response(hal_api_docs_for_one_researcher):
    """ Return the list of dictionaries references from hal response"""
    return hal_api_docs_for_one_researcher['response']['docs']


@pytest.mark.asyncio
async def test_convert(hal_api_cleaned_response):
    """ Test that the converter will return normalised references"""
    test = HalReferencesConverter()

    expected_titles = ["Where does « Axial breakthrough » take place? In the past, or in present narratives of the past?"]
    expected_subjects = [
          "Antiquity",
          "Historiography",
          "Greek city",
          "Vernant",
          "Narration of the past"
        ]
    expected_subtitles = ['test_placeholder_subtitle']
    expected_docid = "1387023"

    for doc in hal_api_cleaned_response:
        test_reference = await test.convert(doc)

        test_titles = [title.value for title in test_reference.titles]
        test_subtitles = [subtitles.value for subtitles in test_reference.subtitles]
        test_subjects = []
        for concept in test_reference.subjects:
            for label in concept.labels:
                test_subjects.append(label.value)

        assert test_titles == expected_titles
        assert test_subjects == expected_subjects
        assert test_subtitles == expected_subtitles
        assert test_reference.source_identifier == expected_docid