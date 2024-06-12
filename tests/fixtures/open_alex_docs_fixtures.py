import pytest

from tests.fixtures.common import _json_data_from_file


@pytest.fixture(name="open_alex_api_work")
def fixture_open_alex_api_work(_base_path) -> dict:
    """
    Generate a OpenAlex API response for work in JSON format
    :param _base_path: test data directory base
    :return: OpenAlex API response for a publication in JSON format
    """
    return _open_alex_api_json_data_from_file(_base_path, "open_alex_work_response")


@pytest.fixture(name="open_alex_work_with_various_locations")
def fixture_open_alex_api_work(_base_path) -> dict:
    """
    Generate a OpenAlex API response for work  with various locations in JSON format
    :param _base_path: test data directory base
    :return: OpenAlex API response for a publication in JSON format
    """
    return _open_alex_api_json_data_from_file(
        _base_path, "open_alex_work_with_various_locations"
    )


@pytest.fixture(name="open_alex_api_work_to_hash")
def fixture_open_alex_api_to_hash(_base_path) -> dict:
    """
    Generate a OpenAlex API response for work in JSON format
    :param _base_path: test data directory base
    :return: OpenAlex API response for one person in JSON format
    """
    return _open_alex_api_json_data_from_file(_base_path, "open_alex_work_to_hash")


@pytest.fixture(name="open_alex_api_work_to_hash_2")
def fixture_open_alex_api_to_hash_2(_base_path) -> dict:
    """
    Generate a OpenAlex API response for work in JSON format
    :param _base_path: test data directory base
    :return: OpenAlex API response for one person in JSON format
    """
    return _open_alex_api_json_data_from_file(_base_path, "open_alex_work_to_hash_2")


def _open_alex_api_json_data_from_file(base_path, file_name) -> dict:
    file_path = f"data/open_alex_api/{file_name}.json"
    return _json_data_from_file(base_path, file_path)
