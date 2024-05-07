import xml.etree.ElementTree as ET
import pytest

from app.harvesters.idref.idref_harvester import IdrefHarvester
from app.harvesters.xml_harvester_raw_result import XMLHarvesterRawResult
from tests.fixtures.common import _et_from_xml_file


@pytest.fixture(name="open_edition_xml_result_for_doc")
def fixture_open_edition_xml_result_for_doc(
    open_edition_et_xml_for_doc,
) -> XMLHarvesterRawResult:
    """XML from Open Edition file"""
    return XMLHarvesterRawResult(
        payload=open_edition_et_xml_for_doc,
        source_identifier="https://journals.openedition.org/conflits/basictei/756",
        formatter_name=IdrefHarvester.Formatters.OPEN_EDITION,
    )


@pytest.fixture(name="open_edition_et_xml_for_doc")
def fixture_open_edition_et_xml_for_doc(_base_path) -> str:
    """XML from Open Edition file"""
    return _open_edition_et_xml_from_file(_base_path, "open_edition_document")


@pytest.fixture(name="open_edition_xml_invalid_created_format")
def fixture_open_edition_xml_invalid_created_format(
    open_edition_et_xml_invalid_created,
) -> XMLHarvesterRawResult:
    """XML from Open Edition file"""
    return XMLHarvesterRawResult(
        payload=open_edition_et_xml_invalid_created,
        source_identifier="https://journals.openedition.org/conflits/basictei/756",
        formatter_name=IdrefHarvester.Formatters.OPEN_EDITION,
    )


@pytest.fixture(name="open_edition_et_xml_invalid_created")
def fixture_open_edition_et_xml_invalid_created(_base_path) -> str:
    """XML from Open Edition file"""
    return _open_edition_et_xml_from_file(
        _base_path, "open_edition_document_with_invalid_created"
    )


@pytest.fixture(name="open_edition_xml_invalid_issued_format")
def fixture_open_edition_xml_invalid_issued_format(
    open_edition_et_xml_invalid_issued,
) -> XMLHarvesterRawResult:
    """XML from Open Edition file"""
    return XMLHarvesterRawResult(
        payload=open_edition_et_xml_invalid_issued,
        source_identifier="https://journals.openedition.org/conflits/basictei/756",
        formatter_name=IdrefHarvester.Formatters.OPEN_EDITION,
    )


@pytest.fixture(name="open_edition_et_xml_invalid_issued")
def fixture_open_edition_et_xml_invalid_issued(_base_path) -> str:
    """XML from Open Edition file"""
    return _open_edition_et_xml_from_file(
        _base_path, "open_edition_document_with_invalid_issued"
    )


@pytest.fixture(name="open_edition_xml_for_hash_1")
def fixture_open_edition_xml_for_hash_1(_base_path) -> str:
    """XML from Open Edition file"""
    return _open_edition_et_xml_from_file(
        _base_path, "open_edition_document_for_hash_1"
    )


@pytest.fixture(name="open_edition_xml_for_hash_2")
def fixture_open_edition_xml_for_hash_2(_base_path) -> str:
    """XML from Open Edition file"""
    return _open_edition_et_xml_from_file(
        _base_path, "open_edition_document_for_hash_2"
    )


def _open_edition_et_xml_from_file(base_path, file_name) -> ET:
    file_path = f"data/open_edition/{file_name}.xml"
    return _et_from_xml_file(base_path, file_path)
