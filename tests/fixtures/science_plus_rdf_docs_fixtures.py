import pathlib

import pytest
from rdflib import Graph, URIRef

from app.harvesters.idref.idref_harvester import IdrefHarvester
from app.harvesters.rdf_harvester_raw_result import RdfHarvesterRawResult as RdfResult


@pytest.fixture(name="science_plus_rdf_result_for_doc")
def fixture_science_plus_rdf_result_for_doc(science_plus_rdf_graph_for_doc) -> RdfResult:
    """Rdf result from sudo wrapped in a RdfHarvesterRawResult"""
    return RdfResult(
        payload=science_plus_rdf_graph_for_doc,
        source_identifier=URIRef(
            "http://hub.abes.fr/cairn/periodical/autr/2008/issue_autr045/"
            "D33AF39D3B7834E0E053120B220A2036/w"
        ),
        formatter_name=IdrefHarvester.Formatters.SCIENCE_PLUS_RDF.value,
    )


@pytest.fixture(name="science_plus_rdf_graph_for_doc")
def fixture_science_plus_rdf_graph_for_doc(_base_path) -> Graph:
    """Rdf graph from sudoc rdf file"""
    return _science_plus_rdf_graph_from_file(_base_path, "science_plus_document")


@pytest.fixture(name="science_plus_rdf_xml_for_doc")
def fixture_science_plus_rdf_xml_for_doc(_base_path) -> str:
    """Rdf xml from sudoc rdf file"""
    return _rdf_xml_file_content(_base_path, "science_plus_document")


def _science_plus_rdf_graph_from_file(base_path, file_name) -> Graph:
    file_path = f"data/science_plus_rdf/{file_name}.rdf"
    return _rdf_graph_from_xml_file(base_path, file_path)


def _rdf_graph_from_xml_file(base_path, file_path) -> Graph:
    input_data = _rdf_xml_file_content(base_path, file_path)
    return Graph().parse(data=input_data, format="xml")


def _rdf_xml_file_content(base_path, file_path):
    file = pathlib.Path(base_path / file_path)
    with open(file, encoding="utf-8") as xml_file:
        return xml_file.read()
