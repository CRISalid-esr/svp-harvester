import xml.etree.ElementTree as ET
import pathlib
import pytest
from rdflib import URIRef

from app.harvesters.idref.idref_harvester import IdrefHarvester
from app.harvesters.rdf_harvester_raw_result import (
    RdfHarvesterRawResult as RdfResult,
)


@pytest.fixture(name="open_edition_rdf_result_for_doc")
def fixture_open_edition_rdf_result_for_doc(open_edition_et_xml_for_doc) -> RdfResult:
    """XML from Open Edition file"""
    return RdfResult(
        payload=open_edition_et_xml_for_doc,
        source_identifier="https://journals.openedition.org/conflits/basictei/756",
        formatter_name=IdrefHarvester.Formatters.OPEN_EDITION,
    )


@pytest.fixture(name="open_edition_et_xml_for_doc")
def fixture_open_edition_et_xml_for_doc(_base_path) -> str:
    """XML from Open Edition file"""
    return _open_edition_et_xml_from_file(_base_path, "open_edition_document")


def _open_edition_et_xml_from_file(base_path, file_name) -> ET:
    file_path = f"data/open_edition/{file_name}.xml"
    return _et_from_xml_file(base_path, file_path)


def _et_from_xml_file(base_path, file_path) -> ET:
    input_data = _xml_file_content(base_path, file_path)
    return ET.fromstring(input_data)


def _xml_file_content(base_path, file_path):
    file = pathlib.Path(base_path / file_path)
    with open(file, encoding="utf-8") as xml_file:
        return xml_file.read()
