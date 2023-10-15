import pytest_asyncio

from app.db.daos.retrieval_dao import RetrievalDAO


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
