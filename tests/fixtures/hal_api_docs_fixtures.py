import pytest

from tests.fixtures.common import _json_data_from_file


@pytest.fixture(name="hal_api_docs_for_researcher")
def fixture_hal_api_docs_for_researcher(_base_path) -> dict:
    """
    Generate a HAL API response for a researcher in JSON format
    :param _base_path: test data directory base
    :return: HAL API response for one researcher in JSON format
    """
    return _hal_api_json_data_from_file(_base_path, "docs_for_researcher")


@pytest.fixture(name="hal_api_docs_for_researcher_version_1")
def fixture_hal_api_docs_for_researcher_version_1(_base_path) -> dict:
    """
    Generate the first version of the HAL API response for a researcher in JSON format
    :param _base_path: test data directory base
    :return: HAL API response for one researcher in JSON format
    """
    return _hal_api_json_data_from_file(_base_path, "docs_for_researcher_version_1")


@pytest.fixture(name="hal_api_docs_with_contributors_version_1")
def fixture_hal_api_docs_with_contributors_version_1(_base_path) -> dict:
    """
    Generate the first version of the HAL API response
    with contributors for a researcher in JSON format
    :param _base_path: test data directory base
    :return: HAL API response for one researcher in JSON format
    """
    return _hal_api_json_data_from_file(_base_path, "docs_with_contributors_version_1")


@pytest.fixture(name="hal_api_docs_for_researcher_version_2")
def fixture_hal_api_docs_for_researcher_version_2(_base_path) -> dict:
    """
    Generate the second version of the HAL API response for a researcher in JSON format
    with a publication unchanged, a publication updated, a publication created a publication deleted
    :param _base_path: test data directory base
    :return: HAL API response for one researcher in JSON format
    """
    return _hal_api_json_data_from_file(_base_path, "docs_for_researcher_version_2")


@pytest.fixture(name="hal_api_docs_with_contributors_version_2")
def fixture_hal_api_docs_with_contributors_version_2(_base_path) -> dict:
    """
    Generate the second version of the HAL API response
    with contributors for a researcher in JSON format
    :param _base_path: test data directory base
    :return: HAL API response for one researcher in JSON format
    """
    return _hal_api_json_data_from_file(_base_path, "docs_with_contributors_version_2")


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
