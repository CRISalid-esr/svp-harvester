import pytest

from tests.fixtures.common import _json_data_from_file


@pytest.fixture(name="hal_api_docs_for_one_researcher")
def fixture_hal_api_docs_for_one_researcher(_base_path) -> dict:
    """
    Generate a HAL API response for one researcher in JSON format
    :param _base_path: test data directory base
    :return: HAL API response for one researcher in JSON format
    """
    return _hal_api_json_data_from_file(_base_path, "docs_for_one_researcher")


@pytest.fixture(name="hal_api_docs_with_same_kw_twice")
def fixture_hal_api_docs_with_same_kw_twice(_base_path) -> dict:
    """
    Generate a HAL API response for one researcher in JSON format
    :param _base_path: test data directory base
    :return: HAL API response for one researcher in JSON format
    """
    return _hal_api_json_data_from_file(_base_path, "docs_with_same_kw_twice")


def _hal_api_json_data_from_file(base_path, file_name) -> dict:
    file_path = f"data/hal_api/{file_name}.json"
    return _json_data_from_file(base_path, file_path)
