import pathlib

import pytest
from rdflib import Graph


@pytest.fixture(name="idref_rdf_result_for_person")
def fixture_idref_rdf_result_for_person(_base_path) -> str:
    """
    Fixture for the result of the idref concept with id 026675846 as raw xml string
    :param _base_path:  test data directory base path
    :return: raw xml string
    """
    return _idref_rdf_graph_from_file(_base_path, "idref_person")


def _idref_rdf_graph_from_file(base_path, file_name) -> Graph:
    file_path = f"data/idref_people_rdf/{file_name}.rdf"
    return _rdf_graph_from_xml_file(base_path, file_path)


def _rdf_graph_from_xml_file(base_path, file_path) -> Graph:
    input_data = _rdf_xml_file_content(base_path, file_path)
    return Graph().parse(data=input_data, format="xml")


def _rdf_xml_file_content(base_path, file_path):
    file = pathlib.Path(base_path / file_path)
    with open(file, encoding="utf-8") as xml_file:
        return xml_file.read()
