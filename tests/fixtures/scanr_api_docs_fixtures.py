import pytest

from tests.fixtures.common import _json_data_from_file


@pytest.fixture(name="scanr_api_docs_from_person")
def fixture_scanr_api_docs_for_persons(_base_path) -> dict:
    """
    Generate a SCANR API response for a person in JSON format
    :param _base_path: test data directory base
    :return: SCANR API response for one researcher in JSON format
    """
    return _scanr_api_json_data_from_file(_base_path, "scanr_api_person_doc")


@pytest.fixture(name="scanr_api_docs_from_publication")
def fixture_scanr_api_docs_for_publications(_base_path) -> dict:
    """
    Generate a SCANR API response for a person in JSON format
    :param _base_path: test data directory base
    :return: SCANR API response for one researcher in JSON format
    """
    return _scanr_api_json_data_from_file(_base_path, "scanr_api_publication_doc")


@pytest.fixture(name="scanr_api_docs_from_publication_with_default_dupe")
def fixture_scanr_api_docs_for_publications_dupe(_base_path) -> dict:
    """
    Generate a SCANR API response for a person in JSON format
    :param _base_path: test data directory base
    :return: SCANR API response for one researcher in JSON format
    """
    return _scanr_api_json_data_from_file(
        _base_path, "scanr_api_publication_with_default_dupe_doc"
    )


@pytest.fixture(name="scanr_api_docs_from_publication_for_authors_dupe")
def fixture_scanr_api_docs_for_authors_dupe(_base_path) -> dict:
    """
    Generate a SCANR API response for a publication in JSON format
    :param _base_path: test data directory base
    :return: SCANR API response for one publication in JSON format
    """
    return _scanr_api_json_data_from_file(
        _base_path, "scanr_api_publication_authors_dupe"
    )


def _scanr_api_json_data_from_file(base_path, file_name) -> dict:
    file_path = f"data/scanr_api/{file_name}.json"
    return _json_data_from_file(base_path, file_path)
