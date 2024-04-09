import pytest

from app.harvesters.json_harvester_raw_result import JsonHarvesterRawResult
from app.harvesters.scanr.scanr_references_converter import ScanrReferencesConverter


@pytest.fixture(name="scanr_publication_doc_book")
def fixture_scanr_publication_doc_book(scanr_publication_doc_book):
    """Return the list of dictionaries references from scanr response"""
    return scanr_publication_doc_book["hits"]["hits"]


async def test_convert_publication_with_book(scanr_publication_doc_book):
    """
    Test that the converter will return normalised references with book information
    """
    converter_under_tests = ScanrReferencesConverter()

    expected_title = "Bulletin de la Société préhistorique française"
    expected_publisher = "Société préhistorique française"

    for doc in scanr_publication_doc_book:
        result = JsonHarvesterRawResult(
            source_identifier=doc.get("_id"), payload=doc, formatter_name="SCANR"
        )

        test_reference = converter_under_tests.build(raw_data=result)
        await converter_under_tests.convert(raw_data=result, new_ref=test_reference)

        book = test_reference.book
        assert expected_title in book.title
        assert expected_publisher in book.publisher
