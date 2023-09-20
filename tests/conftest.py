"""
Fixtures for all tests
"""
import asyncio
import json
import pathlib
from os import environ

import pytest
import pytest_asyncio
from _pytest.logging import LogCaptureFixture
from fastapi import FastAPI
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from starlette.testclient import TestClient

from app.db.daos import RetrievalDAO, HarvestingDAO
from app.db.models import (
    Person as DbPerson,
    Identifier as DbIdentifier,
    State,
)
from app.db.session import Base, engine
from app.models.identifiers import IdentifierTypeEnum
from app.models.people import Person as PydanticPerson

environ["APP_ENV"] = "TEST"


@pytest.fixture(name="test_app")
def app() -> FastAPI:
    """Provide app as fixture"""
    # pylint: disable=import-outside-toplevel
    from app.main import SvpHarvester  # local import for testing purpose

    return SvpHarvester()


@pytest.fixture(name="test_client")
def fixture_test_client(test_app: FastAPI) -> TestClient:
    """Provide test client as fixture"""
    return TestClient(test_app)


@pytest.fixture(autouse=True, name="event_loop")
def fixture_event_loop():
    """Provide an event loop for all tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(autouse=True, name="async_session")
async def fixture_async_session() -> AsyncSession:
    """Provide an async db session for all tests"""
    session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with session() as test_session:
        async with engine.begin() as test_connexion:
            await test_connexion.run_sync(Base.metadata.create_all)

        yield test_session

    async with engine.begin() as test_connexion:
        await test_connexion.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture(name="_base_path")
def fixture_base_path() -> pathlib.Path:
    """Get the current folder of the test"""
    return pathlib.Path(__file__).parent


@pytest.fixture(name="person_without_identifiers")
def fixture_person_without_identifiers(person_without_identifiers_json):
    """
    Generate a person with only first name and last name in Pydantic format
    :return: person with only first name and last name in Pydantic format
    """
    return _person_from_json_data(person_without_identifiers_json)


@pytest.fixture(name="person_without_identifiers_json")
def fixture_person_without_identifiers_json(_base_path):
    """
    Generate a person with only first name and last name in JSON format
    :param _base_path: test data directory base
    :return: person with only first name and last name in JSON format
    """
    return _json_from_file(_base_path, "person_without_identifier")


@pytest.fixture(name="person_with_name_and_idref_db_model")
def fixture_person_with_name_and_idref_db_model():
    """
    Generate a person with first name, last name and IDREF in DB model format
    :return: person with first name, last name and IDREF  in DB model format
    """
    return DbPerson(
        first_name="John",
        last_name="Doe",
        identifiers=[DbIdentifier(type=IdentifierTypeEnum.IDREF, value="123456789")],
    )


@pytest_asyncio.fixture(name="retrieval_db_model")
async def fixture_retrieval_db_model(
    async_session, person_with_name_and_idref_db_model
):
    """
    Generate a retrieval with a person with first name, last name and IDREF in DB model format

    :param async_session: async db session
    :param person_with_name_and_idref_db_model: person  in DB model format
    :return: retrieval with a person with first name, last name and IDREF  in DB model format
    """
    return await RetrievalDAO(async_session).create_retrieval(
        person_with_name_and_idref_db_model
    )


@pytest_asyncio.fixture(name="harvesting_db_model")
async def fixture_harvesting_db_model(async_session, retrieval_db_model):
    """
    Generate a harvesting with a retrieval in DB model format

    :param async_session: async db session
    :param retrieval_db_model: retrieval in DB model format
    :return:  harvesting in DB model format
    """
    return await HarvestingDAO(async_session).create_harvesting(
        retrieval_db_model, "idref", State.RUNNING
    )


@pytest.fixture(name="person_with_name_and_idref")
def fixture_person_with_name_and_idref(person_with_name_and_idref_json):
    """
    Generate a person with first name, last name and IDREF in Pydantic format
    :return: person with first name, last name and IDREF  in Pydantic format
    """
    return _person_from_json_data(person_with_name_and_idref_json)


@pytest.fixture(name="person_with_name_and_id_hal_i")
def fixture_person_with_name_and_id_hal_i(person_with_name_and_id_hal_i_json):
    """
    Generate a person with first name, last name and ID_HAL_I in Pydantic format
    :return: person with first name, last name and ID_HAL_I  in Pydantic format
    """
    return _person_from_json_data(person_with_name_and_id_hal_i_json)


@pytest.fixture(name="person_with_name_and_idref_json")
def fixture_person_with_name_and_idref_json(_base_path):
    """
    Generate a person with first name, last name and IDREF in Json format
    :param _base_path: test data directory base
    :return: person with first name, last name and IDREF in Json format
    """
    return _json_from_file(_base_path, "person_with_name_and_idref")


@pytest.fixture(name="person_with_name_and_id_hal_i_json")
def fixture_person_with_name_and_id_hal_i_json(_base_path):
    """
    Generate a person with first name, last name and ID_HAL_I in Json format
    :param _base_path: test data directory base
    :return: person with first name, last name and ID_HAL_I in Json format
    """
    return _json_from_file(_base_path, "person_with_name_and_id_hal_i")


@pytest.fixture(name="person_with_last_name_only")
def fixture_person_with_last_name_only(person_with_last_name_only_json):
    """
    Generate a person with  last name only in Pydantic format
    :param person_with_last_name_only_json: person with last name only in json format
    :return: person with last name only in Pydantic format
    """
    return _person_from_json_data(person_with_last_name_only_json)


@pytest.fixture(name="person_with_last_name_and_first_name")
def fixture_person_with_last_name_and_first_name(
    person_with_last_name_and_first_name_json,
):
    """
    Generate a person with first name and last name in Pydantic format
    :param person_with_last_name_and_first_name_json: person in json format
    :return: person with first name and last name in Pydantic format
    """
    return _person_from_json_data(person_with_last_name_and_first_name_json)


@pytest.fixture(name="person_with_last_name_only_json")
def fixture_person_with_last_name_only_json(_base_path):
    """
    Generate a person with only last name in JSON format
    :param _base_path: test data directory base
    :return: person with only last name in JSON format
    """
    return _json_from_file(_base_path, "person_with_last_name_only")


@pytest.fixture(name="person_with_last_name_and_first_name_json")
def fixture_person_with_last_name_and_first_name_json(_base_path):
    """
    Generate a person with first name and last name in JSON format
    :param _base_path: test data directory base
    :return: person with first name and last name in JSON format
    """
    return _json_from_file(_base_path, "person_with_last_name_and_first_name")


def _person_from_json_data(input_data):
    return PydanticPerson(**input_data)


def _json_from_file(base_path, person):
    file = pathlib.Path(base_path / f"data/people/{person}.json")
    with open(file, encoding="utf-8") as json_file:
        input_data = json_file.read()
    return json.loads(input_data)


@pytest.fixture(autouse=True)
def caplog(caplog: LogCaptureFixture):  # pylint: disable=redefined-outer-name
    """
    Make pytest work with loguru. See:
    https://loguru.readthedocs.io/en/stable/resources/migration.html#making-things-work-with-pytest-and-caplog

    :param caplog: pytest fixture
    :return: loguru compatible caplog
    """
    handler_id = logger.add(
        caplog.handler,
        format="{message}",
        level=0,
        filter=lambda record: record["level"].no >= caplog.handler.level,
        enqueue=True,
    )
    yield caplog
    logger.remove(handler_id)
