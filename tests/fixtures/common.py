import json
import pathlib

import pytest

from app.models.people import Person as PydanticPerson


@pytest.fixture(name="_base_path")
def fixture_base_path() -> pathlib.Path:
    """Get the current folder of the test"""
    return pathlib.Path(__file__).parent.parent


def _json_data_from_file(base_path, file_path) -> dict:
    file = pathlib.Path(base_path / file_path)
    with open(file, encoding="utf-8") as json_file:
        input_data = json_file.read()
    return json.loads(input_data)


def _person_json_data_from_file(base_path, person):
    file_path = f"data/people/{person}.json"
    return _json_data_from_file(base_path, file_path)


def _person_from_json_data(input_data):
    return PydanticPerson(**input_data)
