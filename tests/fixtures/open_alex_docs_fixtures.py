import pytest

from tests.fixtures.common import _json_data_from_file


@pytest.fixture(name="open_alex_api_work")
def fixture_open_alex_api_work(_base_path) -> dict:
    """
    Generate a OpenAlex API response for work in JSON format
    :param _base_path: test data directory base
    :return: OpenAlex API response for one person in JSON format
    """
    return _open_alex_api_json_data_from_file(_base_path, "open_alex_work_response")


def _open_alex_api_json_data_from_file(base_path, file_name) -> dict:
    file_path = f"data/open_alex_api/{file_name}.json"
    return _json_data_from_file(base_path, file_path)
