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

from app.db.daos.retrieval_dao import RetrievalDAO
from app.db.daos.harvesting_dao import HarvestingDAO
from app.db.models.harvesting_model import Harvesting
from app.db.models.identifier_model import Identifier as DbIdentifier
from app.db.models.person_model import Person as DbPerson
from app.db.session import Base, engine
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
    return _person_json_data_from_file(_base_path, "person_without_identifier")


@pytest.fixture(name="person_with_full_name_only")
def fixture_person_with_full_name_only(person_with_full_name_only_json):
    """
    Generate a person with only first name and last name in Pydantic format
    :return: person with only first name and last name in Pydantic format
    """
    return _person_from_json_data(person_with_full_name_only_json)


@pytest.fixture(name="person_with_full_name_only_json")
def fixture_person_with_full_name_only_json(_base_path):
    """
    Generate a person with only first name and last name in JSON format
    :param _base_path: test data directory base
    :return: person with only first name and last name in JSON format
    """
    return _person_json_data_from_file(_base_path, "person_with_full_name_only")


@pytest.fixture(name="person_with_name_and_idref_db_model")
def fixture_person_with_name_and_idref_db_model():
    """
    Generate a person with first name, last name and IDREF in DB model format
    :return: person with first name, last name and IDREF  in DB model format
    """
    return DbPerson(
        first_name="John",
        last_name="Doe",
        identifiers=[DbIdentifier(type="idref", value="123456789")],
    )


@pytest.fixture(name="person_with_name_and_id_hal_i_db_model")
def fixture_person_with_name_and_id_hal_i_db_model():
    """
    Generate a person with first name, last name and Id_Hal_i in DB model format
    :return: person with first name, last name and Id_Hal_i  in DB model format
    """
    return DbPerson(
        first_name="John",
        last_name="Doe",
        identifiers=[DbIdentifier(type="id_hal_i", value="123456789")],
    )


@pytest.fixture(name="person_with_name_and_id_hal_s_db_model")
def fixture_person_with_name_and_id_hal_s_db_model():
    """
    Generate a person with first name, last name and Id_Hal_s in DB model format
    :return: person with first name, last name and Id_Hal_s  in DB model format
    """
    return DbPerson(
        first_name="John",
        last_name="Doe",
        identifiers=[DbIdentifier(type="id_hal_s", value="john-doe")],
    )


@pytest.fixture(name="person_with_name_and_id_hal_i_s_db_model")
def fixture_person_with_name_and_id_hal_i_s_db_model():
    """
    Generate a person with first name, last name and Id_Hal_i and Id_Hal_s in DB model format
    :return: person with first name, last name and Id_Hal_i and Id_Hal_s  in DB model format
    """
    return DbPerson(
        first_name="John",
        last_name="Doe",
        identifiers=[
            DbIdentifier(type="id_hal_i", value="123456789"),
            DbIdentifier(type="id_hal_s", value="john-doe"),
        ],
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


@pytest_asyncio.fixture(name="retrieval_db_model_for_person_with_id_hal_i")
async def fixture_retrieval_db_model_for_person_with_id_hal_i(
        async_session, person_with_name_and_id_hal_i_db_model
):
    """
    Generate a retrieval with a person with first name, last name and ID_HAL_I in DB model format

    :param async_session: async db session
    :param person_with_name_and_id_hal_i_db_model: person  in DB model format
    :return: retrieval with a person with first name, last name and ID_HAL_I  in DB model format
    """
    return await RetrievalDAO(async_session).create_retrieval(
        person_with_name_and_id_hal_i_db_model
    )


@pytest_asyncio.fixture(name="retrieval_db_model_for_person_with_id_hal_s")
async def fixture_retrieval_db_model_for_person_with_id_hal_s(
        async_session, person_with_name_and_id_hal_s_db_model
):
    """
    Generate a retrieval with a person with first name, last name and ID_HAL_S in DB model format

    :param async_session: async db session
    :param person_with_name_and_id_hal_s_db_model: person  in DB model format
    :return: retrieval with a person with first name, last name and ID_HAL_S  in DB model format
    """
    return await RetrievalDAO(async_session).create_retrieval(
        person_with_name_and_id_hal_s_db_model
    )


@pytest_asyncio.fixture(name="retrieval_db_model_for_person_with_id_hal_i_s")
async def fixture_retrieval_db_model_for_person_with_id_hal_i_s(
        async_session, person_with_name_and_id_hal_i_s_db_model
):
    """
    Generate a retrieval with a person with first name, last name, ID_HAL_I and ID_HAL_S

    :param async_session: async db session
    :param person_with_name_and_id_hal_i_s_db_model: person  in DB model format
    :return: retrieval with a person with first name, last name and ID_HAL_I  ID_HAL_S
    """
    return await RetrievalDAO(async_session).create_retrieval(
        person_with_name_and_id_hal_i_s_db_model
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
        retrieval_db_model, "idref", Harvesting.State.RUNNING
    )


@pytest_asyncio.fixture(name="hal_harvesting_db_model_id_hal_i")
async def fixture_hal_harvesting_db_model_id_hal_i(
        async_session, retrieval_db_model_for_person_with_id_hal_i
):
    """
    Generate a Hal harvesting with a retrieval in DB model format for person with ID_HAL_I

    :param async_session: async db session
    :param retrieval_db_model_for_person_with_id_hal_i: retrieval in DB model format
    :return:  Hal harvesting in DB model format
    """
    return await HarvestingDAO(async_session).create_harvesting(
        retrieval_db_model_for_person_with_id_hal_i, "hal", Harvesting.State.RUNNING
    )


@pytest_asyncio.fixture(name="hal_harvesting_db_model_id_hal_s")
async def fixture_hal_harvesting_db_model_id_hal_s(
        async_session, retrieval_db_model_for_person_with_id_hal_s
):
    """
    Generate a Hal harvesting with a retrieval in DB model format for person with ID_HAL_I

    :param async_session: async db session
    :param retrieval_db_model_for_person_with_id_hal_s: retrieval in DB model format
    :return:  Hal harvesting in DB model format
    """
    return await HarvestingDAO(async_session).create_harvesting(
        retrieval_db_model_for_person_with_id_hal_s, "hal", Harvesting.State.RUNNING
    )


@pytest_asyncio.fixture(name="hal_harvesting_db_model_id_hal_i_s")
async def fixture_hal_harvesting_db_model_id_hal_i_s(
        async_session, retrieval_db_model_for_person_with_id_hal_i_s
):
    """
    Generate a Hal harvesting with a retrieval in DB model format for person with ID_HAL_I

    :param async_session: async db session
    :param retrieval_db_model_for_person_with_id_hal_i_s: retrieval in DB model format
    :return:  Hal harvesting in DB model format
    """
    return await HarvestingDAO(async_session).create_harvesting(
        retrieval_db_model_for_person_with_id_hal_i_s, "hal", Harvesting.State.RUNNING
    )


@pytest_asyncio.fixture(name="hal_harvesting_db_model_id_hal_s")
async def fixture_hal_harvesting_db_model_id_hal_s(
    async_session, retrieval_db_model_for_person_with_id_hal_s
):
    """
    Generate a Hal harvesting with a retrieval in DB model format for person with ID_HAL_I

    :param async_session: async db session
    :param retrieval_db_model_for_person_with_id_hal_s: retrieval in DB model format
    :return:  Hal harvesting in DB model format
    """
    return await HarvestingDAO(async_session).create_harvesting(
        retrieval_db_model_for_person_with_id_hal_s, "hal", State.RUNNING
    )


@pytest_asyncio.fixture(name="hal_harvesting_db_model_id_hal_i_s")
async def fixture_hal_harvesting_db_model_id_hal_i_s(
    async_session, retrieval_db_model_for_person_with_id_hal_i_s
):
    """
    Generate a Hal harvesting with a retrieval in DB model format for person with ID_HAL_I

    :param async_session: async db session
    :param retrieval_db_model_for_person_with_id_hal_i_s: retrieval in DB model format
    :return:  Hal harvesting in DB model format
    """
    return await HarvestingDAO(async_session).create_harvesting(
        retrieval_db_model_for_person_with_id_hal_i_s, "hal", State.RUNNING
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


@pytest.fixture(name="person_with_name_and_id_hal_s")
def fixture_person_with_name_and_id_hal_s(person_with_name_and_id_hal_s_json):
    """
    Generate a person with first name, last name and ID_HAL_I in Pydantic format
    :return: person with first name, last name and ID_HAL_I  in Pydantic format
    """
    return _person_from_json_data(person_with_name_and_id_hal_s_json)


@pytest.fixture(name="person_with_name_and_idref_json")
def fixture_person_with_name_and_idref_json(_base_path):
    """
    Generate a person with first name, last name and IDREF in Json format
    :param _base_path: test data directory base
    :return: person with first name, last name and IDREF in Json format
    """
    return _person_json_data_from_file(_base_path, "person_with_name_and_idref")


@pytest.fixture(name="person_with_name_and_unknown_identifier_type_json")
def fixture_person_with_name_and_unknown_identifier_type_json(_base_path):
    """
    Generate a person with first name, last name and unknown identifier type in Json format
    :param _base_path: test data directory base
    :return: person with first name, last name and unknown identifier type in Json format
    """
    return _person_json_data_from_file(
        _base_path, "person_with_name_and_unknown_identifier_type"
    )


@pytest.fixture(name="person_with_name_and_id_hal_i_json")
def fixture_person_with_name_and_id_hal_i_json(_base_path):
    """
    Generate a person with first name, last name and ID_HAL_I in Json format
    :param _base_path: test data directory base
    :return: person with first name, last name and ID_HAL_I in Json format
    """
    return _person_json_data_from_file(_base_path, "person_with_name_and_id_hal_i")


@pytest.fixture(name="person_with_name_and_id_hal_s_json")
def fixture_person_with_name_and_id_hal_s_json(_base_path):
    """
    Generate a person with first name, last name and ID_HAL_S in Json format
    :param _base_path: test data directory base
    :return: person with first name, last name and ID_HAL_S in Json format
    """
    return _person_json_data_from_file(_base_path, "person_with_name_and_id_hal_s")


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
    return _person_json_data_from_file(_base_path, "person_with_last_name_only")


@pytest.fixture(name="person_with_last_name_and_first_name_json")
def fixture_person_with_last_name_and_first_name_json(_base_path):
    """
    Generate a person with first name and last name in JSON format
    :param _base_path: test data directory base
    :return: person with first name and last name in JSON format
    """
    return _person_json_data_from_file(
        _base_path, "person_with_last_name_and_first_name"
    )


def _person_from_json_data(input_data):
    return PydanticPerson(**input_data)


def _person_json_data_from_file(base_path, person):
    file_path = f"data/people/{person}.json"
    return _json_data_from_file(base_path, file_path)


@pytest.fixture(name="hal_api_docs_for_one_researcher")
def fixture_hal_api_docs_for_one_researcher(_base_path):
    """
    Generate a HAL API response for one researcher in JSON format
    :param _base_path: test data directory base
    :return: HAL API response for one researcher in JSON format
    """
    return _hal_api_json_data_from_file(_base_path, "docs_for_one_researcher")


@pytest.fixture(name="hal_api_docs_with_same_kw_twice")
def fixture_hal_api_docs_with_same_kw_twice(_base_path):
    """
    Generate a HAL API response for one researcher in JSON format
    :param _base_path: test data directory base
    :return: HAL API response for one researcher in JSON format
    """
    return _hal_api_json_data_from_file(_base_path, "docs_with_same_kw_twice")


def _hal_api_json_data_from_file(base_path, file_name):
    file_path = f"data/hal_api/{file_name}.json"
    return _json_data_from_file(base_path, file_path)


def _json_data_from_file(base_path, file_path):
    file = pathlib.Path(base_path / file_path)
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
