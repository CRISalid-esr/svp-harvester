import pytest

from tests.fixtures.common import _json_data_from_file


@pytest.fixture(name="jel_sparql_endpoint_response_for_concept")
def fixture_jel_sparql_endpoint_response_for_concept(_base_path) -> dict:
    """
    Generate an Idref Sparql endpoint response with Idref publications in JSON format

    :param _base_path: test data directory base
    :return: Idref Sparql endpoint response for one researcher in JSON format
    """
    return _jel_fuseki_sparql_endpoint_json_results_from_file(
        _base_path, "jel_sparql_endpoint_response_for_concept"
    )


def _jel_fuseki_sparql_endpoint_json_results_from_file(base_path, file_name) -> dict:
    file_path = f"data/jel_sparql_endpoint/{file_name}.json"
    return _json_data_from_file(base_path, file_path)
