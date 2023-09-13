"""
Fixtures for all tests
"""
import json
import pathlib
from os import environ

import pytest
from fastapi import FastAPI
from starlette.testclient import TestClient

from app.models.people import Person

environ["APP_ENV"] = "TEST"


@pytest.fixture(name="test_app")
def app() -> FastAPI:
    """Provide app as fixture"""
    # pylint: disable=import-outside-toplevel
    from app.main import get_application  # local import for testing purpose

    return get_application()


@pytest.fixture
def test_client(test_app: FastAPI) -> TestClient:
    """Provide test client as fixture"""
    return TestClient(test_app)


@pytest.fixture
def _base_path() -> pathlib.Path:
    """Get the current folder of the test"""
    return pathlib.Path(__file__).parent


@pytest.fixture
def person_without_identifiers(_base_path):
    """
    Generate a person with only first name and last name
    :param _base_path: test data directory base
    :return: person with only first name and last name
    """
    return _person_from_json_file(_base_path, "person_without_identifier")


@pytest.fixture
def person_with_name_and_idref(_base_path):
    """
    Generate a person with first name, last name and IDREF
    :param _base_path: test data directory base
    :return: person with first name, last name and IDREF
    """
    return _person_from_json_file(_base_path, "person_with_name_and_idref")


@pytest.fixture
def person_person_with_last_name_only(_base_path):
    """
    Generate a person with only last name
    :param _base_path: test data directory base
    :return: person with only first name and last name
    """
    return _person_from_json_file(_base_path, "person_with_last_name_only")


def _person_from_json_file(base_path, person):
    file = pathlib.Path(base_path / f"data/people/{person}.json")
    with open(file, encoding="utf-8") as json_file:
        input_data = json_file.read()
    return Person(**json.loads(input_data))
