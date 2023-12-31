import pytest

from tests.fixtures.common import _json_data_from_file


@pytest.fixture(name="idref_sparql_endpoint_results_with_idref_pubs")
def fixture_idref_sparql_endpoint_results_with_idref_pubs(_base_path) -> dict:
    """
    Generate an Idref Sparql endpoint response with Idref publications in JSON format

    :param _base_path: test data directory base
    :return: Idref Sparql endpoint response for one researcher in JSON format
    """
    return _idref_sparql_endpoint_json_results_from_file(
        _base_path, "idref_result_with_idref_references"
    )


@pytest.fixture(name="idref_sparql_endpoint_results_with_sudoc_pub")
def fixture_idref_sparql_endpoint_results_with_sudoc_pub(_base_path) -> dict:
    """
    Generate an Idref Sparql endpoint response with Sudoc publication in JSON format

    :param _base_path: test data directory base
    :return: Idref Sparql endpoint response for one researcher in JSON format
    """
    return _idref_sparql_endpoint_json_results_from_file(
        _base_path, "idref_result_with_sudoc_reference"
    )


def _idref_sparql_endpoint_json_results_from_file(base_path, file_name) -> dict:
    file_path = f"data/idref_sparql_endpoint/{file_name}.json"
    return _json_data_from_file(base_path, file_path)
