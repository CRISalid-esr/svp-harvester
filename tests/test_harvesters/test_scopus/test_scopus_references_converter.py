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

    expected_title = (
        "Is musculoskeletal pain associated with increased muscle stiffness?"
    )

    expected_abstract = "Introduction and Aims: Approximately 21% of the world's"
    expected_identifier = ["10.1111/cpf.12870", "14750961", "38155545"]
    expected_document_type = "Review"
    expected_concepts = [
        "imaging methods",
        "muscle",
        "musculoskeletal pain",
        "shear wave elastography",
        "stiffness",
    ]
    expected_authors = [
        "Haueise A.",
        "Le Sant G.",
        "Eisele-Metzger A.",
        "Dieterich A.V.",
    ]
    expected_affiliation = ["Hochschule Furtwangen", "CHU de Nantes"]

    assert test_reference.titles[0].value == expected_title
    assert test_reference.abstracts[0].value == expected_abstract
    for identifier in test_reference.identifiers:
        assert identifier.value in expected_identifier
    assert test_reference.document_type[0].label == expected_document_type
    for concept in test_reference.subjects:
        for label in concept.labels:
            assert label.value in expected_concepts
    for contribution in test_reference.contributions:
        assert contribution.contributor.name in expected_authors
        assert contribution.role == "Author"
        for affiliation in contribution.affiliations:
            assert affiliation.name in expected_affiliation
