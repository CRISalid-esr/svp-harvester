import pathlib

import pytest


@pytest.fixture(name="idref_rdf_raw_result_for_concept")
def fixture_idref_rdf_raw_result_for_concept(_base_path) -> str:
    """
    Fixture for the result of the idref concept with id 082303363 as raw xml string
    :param _base_path:  test data directory base path
    :return: raw xml string
    """
    return _idref_concepts_raw_rdf_from_file(_base_path, "idref_concept")


def _idref_concepts_raw_rdf_from_file(base_path, file_name) -> str:
    file_path = f"data/idref_concepts_rdf/{file_name}.rdf"
    return _rdf_xml_file_content(base_path, file_path)


def _rdf_xml_file_content(base_path, file_path):
    file = pathlib.Path(base_path / file_path)
    with open(file, encoding="utf-8") as xml_file:
        return xml_file.read()
