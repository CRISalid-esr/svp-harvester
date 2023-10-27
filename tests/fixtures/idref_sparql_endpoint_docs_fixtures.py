import pytest

from tests.fixtures.common import _json_data_from_file


@pytest.fixture(name="idref_sparql_endpoint_results_with_one_idref_pub")
def fixture_idref_sparql_endpoint_results_with_one_idref_pub(_base_path) -> dict:
    """
    Generate a Idref Sparql endpoint response for one researcher in JSON format

    :param _base_path: test data directory base
    :return: Idref Sparql endpoint response for one researcher in JSON format
    """
    return _idref_sparql_endpoint_json_results_from_file(
        _base_path, "results_for_researcher"
    )


def _idref_sparql_endpoint_json_results_from_file(base_path, file_name) -> dict:
    file_path = f"data/idref_sparql_endpoint/{file_name}.json"
    return _json_data_from_file(base_path, file_path)
