"""
Fixtures for all tests
"""
import asyncio
import json
import pathlib
from os import environ

import pytest
import pytest_asyncio
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from starlette.testclient import TestClient

from app.db.session import Base, engine
from app.models.people import Person

environ["APP_ENV"] = "TEST"


@pytest.fixture(name="test_app")
def app(event_loop) -> FastAPI:
    """Provide app as fixture"""
    # pylint: disable=import-outside-toplevel
    from app.main import get_application  # local import for testing purpose

    return get_application()


@pytest.fixture
def test_client(test_app: FastAPI) -> TestClient:
    """Provide test client as fixture"""
    return TestClient(test_app)


@pytest.fixture(autouse=True)
def event_loop(request):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(autouse=True)
async def async_session(event_loop) -> AsyncSession:
    session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with session() as s:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        yield s

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
def _base_path() -> pathlib.Path:
    """Get the current folder of the test"""
    return pathlib.Path(__file__).parent


@pytest.fixture
def person_without_identifiers(person_without_identifiers_json):
    """
    Generate a person with only first name and last name in Pydantic format
    :return: person with only first name and last name in Pydantic format
    """
    return _person_from_json_data(person_without_identifiers_json)


@pytest.fixture
def person_without_identifiers_json(_base_path):
    """
    Generate a person with only first name and last name in JSON format
    :param _base_path: test data directory base
    :return: person with only first name and last name in JSON format
    """
    return _json_from_file(_base_path, "person_without_identifier")


@pytest.fixture
def person_with_name_and_idref(person_with_name_and_idref_json):
    """
    Generate a person with first name, last name and IDREF in Pydantic format
    :return: person with first name, last name and IDREF  in Pydantic format
    """
    return _person_from_json_data(person_with_name_and_idref_json)


@pytest.fixture
def person_with_name_and_idref_json(_base_path):
    """
    Generate a person with first name, last name and IDREF in JSON format
    :param _base_path: test data directory base
    """
    return _json_from_file(_base_path, "person_with_name_and_idref")


@pytest.fixture
def person_with_last_name_only(person_with_last_name_only_json):
    """
    Generate a person with only last name in Pydantic format
    :return: person with only first name and last name in Pydantic format
    """
    return _person_from_json_data(person_with_last_name_only_json)


@pytest.fixture
def person_with_last_name_only_json(_base_path):
    """
    Generate a person with only last name in JSON format
    :param _base_path: test data directory base
    :return: person with only first name and last name in JSON format
    """
    return _json_from_file(_base_path, "person_with_last_name_only")


def _person_from_json_data(input_data):
    return Person(**input_data)


def _json_from_file(base_path, person):
    file = pathlib.Path(base_path / f"data/people/{person}.json")
    with open(file, encoding="utf-8") as json_file:
        input_data = json_file.read()
    return json.loads(input_data)
