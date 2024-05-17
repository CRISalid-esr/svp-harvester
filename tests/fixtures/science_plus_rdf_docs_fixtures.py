import pathlib

import pytest
from rdflib import Graph, URIRef

from app.harvesters.idref.idref_harvester import IdrefHarvester
from app.harvesters.rdf_harvester_raw_result import RdfHarvesterRawResult as RdfResult


@pytest.fixture(name="science_plus_rdf_result_without_title")
def fixture_science_plus_rdf_result_without_title(
    science_plus_rdf_graph_for_doc_without_title,
) -> RdfResult:
    """Rdf result from science plus wrapped in a RdfHarvesterRawResult without title"""
    return RdfResult(
        payload=science_plus_rdf_graph_for_doc_without_title,
        source_identifier=URIRef(
            "http://hub.abes.fr/cairn/periodical/autr/2008/issue_autr045/"
            "D33AF39D3B7834E0E053120B220A2036/w"
        ),
        formatter_name=IdrefHarvester.Formatters.SCIENCE_PLUS_RDF.value,
    )


@pytest.fixture(name="science_plus_rdf_result_for_doc")
def fixture_science_plus_rdf_result_for_doc(
    science_plus_rdf_graph_for_doc,
) -> RdfResult:
    """Rdf result from science plus wrapped in a RdfHarvesterRawResult"""
    return RdfResult(
        payload=science_plus_rdf_graph_for_doc,
        source_identifier=URIRef(
            "http://hub.abes.fr/cairn/periodical/autr/2008/issue_autr045/"
            "D33AF39D3B7834E0E053120B220A2036/w"
        ),
        formatter_name=IdrefHarvester.Formatters.SCIENCE_PLUS_RDF.value,
    )


@pytest.fixture(name="science_plus_rdf_graph_for_doc_without_title")
def fixture_science_plus_rdf_graph_for_doc_without_title(_base_path) -> Graph:
    """Rdf graph from science plus rdf file without title"""
    return _science_plus_rdf_graph_from_file(
        _base_path, "science_plus_document_without_title"
    )


@pytest.fixture(name="science_plus_rdf_graph_for_doc")
def fixture_science_plus_rdf_graph_for_doc(_base_path) -> Graph:
    """Rdf graph from science plus rdf file"""
    return _science_plus_rdf_graph_from_file(_base_path, "science_plus_document")


@pytest.fixture(name="science_plus_rdf_result_for_journal")
def fixture_science_plus_rdf_graph_for_journal(_base_path) -> Graph:
    """Rdf result from science plus rdf journal file"""
    return _science_plus_rdf_graph_from_file(_base_path, "science_plus_journal")


@pytest.fixture(name="science_plus_rdf_result_for_issue")
def fixture_science_plus_rdf_graph_for_issue(_base_path) -> Graph:
    """Rdf result from science plus rdf issue file"""
    return _science_plus_rdf_graph_from_file(_base_path, "science_plus_issue")


@pytest.fixture(name="science_plus_rdf_graph_for_hash_1")
def fixture_science_plus_rdf_graph_for_hash_1(_base_path) -> Graph:
    """Rdf graph from science plus rdf file"""
    return _science_plus_rdf_graph_from_file(
        _base_path, "science_plus_document_for_hash_1"
    )


@pytest.fixture(name="science_plus_rdf_graph_for_hash_2")
def fixture_science_plus_rdf_graph_for_hash_2(_base_path) -> Graph:
    """Rdf graph from science plus rdf file"""
    return _science_plus_rdf_graph_from_file(
        _base_path, "science_plus_document_for_hash_2"
    )


@pytest.fixture(name="science_plus_rdf_xml_for_doc")
def fixture_science_plus_rdf_xml_for_doc(_base_path) -> str:
    """Rdf xml from science plus rdf file"""
    return _rdf_xml_file_content(_base_path, "science_plus_document")


@pytest.fixture(name="science_plus_raw_result_for_concept")
def fixture_science_plus_raw_result_for_concept(_base_path) -> str:
    """Rdf xml from science plus rdf file"""
    return _abes_concepts_raw_rdf_from_file(_base_path, "science_plus_abes_concept")


def _science_plus_rdf_graph_from_file(base_path, file_name) -> Graph:
    file_path = f"data/science_plus_rdf/{file_name}.rdf"
    return _rdf_graph_from_xml_file(base_path, file_path)


def _rdf_graph_from_xml_file(base_path, file_path) -> Graph:
    input_data = _rdf_xml_file_content(base_path, file_path)
    return Graph().parse(data=input_data, format="xml")


def _abes_concepts_raw_rdf_from_file(base_path, file_name) -> str:
    file_path = f"data/science_plus_rdf/{file_name}.rdf"
    return _rdf_xml_file_content(base_path, file_path)


def _rdf_xml_file_content(base_path, file_path):
    file = pathlib.Path(base_path / file_path)
    with open(file, encoding="utf-8") as xml_file:
        return xml_file.read()
