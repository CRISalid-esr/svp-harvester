import pytest
from app.harvesters.scopus.scopus_references_converter import ScopusReferencesConverter

from app.harvesters.xml_harvester_raw_result import XMLHarvesterRawResult


@pytest.mark.asyncio
async def test_convert(scopus_xml_raw_result_for_doc: XMLHarvesterRawResult):
    """Test that the converter will return normalised references"""
    converter_under_test = ScopusReferencesConverter()

    test_reference = converter_under_test.build(raw_data=scopus_xml_raw_result_for_doc)

    await converter_under_test.convert(
        raw_data=scopus_xml_raw_result_for_doc, new_ref=test_reference
    )

    expected_title = "Is musculoskeletal pain associated with increased muscle"

    assert test_reference.titles[0].value == expected_title
