from loguru import logger
import pytest

from app.harvesters.idref.open_edition_references_converter import (
    OpenEditionReferencesConverter,
)


@pytest.mark.asyncio
async def test_open_edition_convert_for_rfd_result(
    open_edition_rdf_result_for_doc,
):
    """
    GIVEN a OpenEditionReferencesConverter instance and a Open Edition XML result for a document
    WHEN the convert method is called
    THEN it should return a Reference instance with the expected values

    :param: open_edition_rdf_result_for_doc: a Open Edition RDF result for a document
    :return: None
    """
    converter_under_tests = OpenEditionReferencesConverter()
    result = await converter_under_tests.convert(open_edition_rdf_result_for_doc)
    expected_french_title = "Les émeutes entre hindous et musulmans (partie 2)"
    expected_french_abstract_beginning = (
        "Si le caractère très ancien et les facteurs religieux des émeutes"
    )
    expected_reference_identifier = [
        "https://journals.openedition.org/conflits/756",
        "10.4000/conflits.756",
    ]

    assert result.source_identifier == str(
        open_edition_rdf_result_for_doc.source_identifier
    )
    assert len(result.titles) == 1
    assert expected_french_title in [title.value for title in result.titles]
    assert any(
        abstract.value.startswith(expected_french_abstract_beginning)
        for abstract in result.abstracts
    )
    assert any(
        identifier.value in expected_reference_identifier
        for identifier in result.identifiers
    )
    assert result.document_type[0].label == "Article"
