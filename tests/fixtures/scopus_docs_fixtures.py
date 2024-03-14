import xml.etree.ElementTree as ET
import pytest
from app.harvesters.scopus.scopus_client import ScopusClient

from app.harvesters.scopus.scopus_harvester import ScopusHarvester
from app.harvesters.xml_harvester_raw_result import XMLHarvesterRawResult
from tests.fixtures.common import _et_from_xml_file, _xml_file_content


@pytest.fixture(name="scopus_xml_raw_result_for_doc")
def fixture_scopus_xml_raw_result_for_doc(scopus_et_for_doc) -> XMLHarvesterRawResult:
    """XML from Scopus file"""

    return XMLHarvesterRawResult(
        payload=scopus_et_for_doc.findall(".//default:entry", ScopusClient.NAMESPACE)[
            0
        ],
        source_identifier="test_id",
        formatter_name=ScopusHarvester.FORMATTER_NAME,
    )


@pytest.fixture(name="scopus_et_for_doc")
def fixture_scopus_et_for_doc(_base_path) -> ET:
    """XML from Scopus file"""
    return _scopus_et_from_file(_base_path, "scopus_document")


@pytest.fixture(name="scopus_xml_doc")
def fixture_scopus_xml_doc(_base_path) -> ET:
    """XML from Scopus file"""
    return _scopus_xml_file_content(_base_path, "scopus_document")


def _scopus_xml_file_content(base_path, file_name) -> ET:
    file_path = f"data/scopus_api/{file_name}.xml"
    return _xml_file_content(base_path, file_path)


def _scopus_et_from_file(base_path, file_name) -> ET:
    file_path = f"data/scopus_api/{file_name}.xml"
    return _et_from_xml_file(base_path, file_path)
