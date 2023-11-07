from typing import List

import pytest_asyncio

from app.db.daos.retrieval_dao import RetrievalDAO
from app.db.models.retrieval import Retrieval as DbRetrieval


@pytest_asyncio.fixture(name="retrieval_db_model_for_person_with_idref")
async def fixture_retrieval_db_model_for_person_with_idref(
    async_session, person_with_name_and_idref_db_model
) -> DbRetrieval:
    """
    Generate a retrieval with a person with first name, last name and IDREF in DB model format

    :param async_session: async db session
    :param person_with_name_and_idref_db_model: person  in DB model format
    :return: retrieval with a person with first name, last name and IDREF  in DB model format
    """
    return await RetrievalDAO(async_session).create_retrieval(
        person_with_name_and_idref_db_model
    )


@pytest_asyncio.fixture(name="two_retrievals_db_models_for_same_person")
async def fixture_two_retrieval_db_models_for_same_person(
    async_session, person_with_name_and_idref_db_model
) -> List[DbRetrieval]:
    """
    Generate two retrievals with a person with first name, last name and IDREF in DB model format

    :param async_session: async db session
    :param person_with_name_and_idref_db_model: person  in DB model format
    :return: two retrievals with a person with first name, last name and IDREF  in DB model format
    """
    retrieval_1 = await RetrievalDAO(async_session).create_retrieval(
        person_with_name_and_idref_db_model
    )
    retrieval_2 = await RetrievalDAO(async_session).create_retrieval(
        person_with_name_and_idref_db_model
    )
    return [retrieval_1, retrieval_2]


@pytest_asyncio.fixture(name="three_retrievals_db_models_for_same_person")
async def fixture_three_retrieval_db_models_for_same_person(
    async_session, person_with_name_and_idref_db_model
) -> List[DbRetrieval]:
    """
    Generate three retrievals with a person with first name, last name and IDREF in DB model format

    :param async_session: async db session
    :param person_with_name_and_idref_db_model: person  in DB model format
    :return: three retrievals with a person with first name, last name and IDREF  in DB model format
    """
    retrieval_1 = await RetrievalDAO(async_session).create_retrieval(
        person_with_name_and_idref_db_model
    )
    retrieval_2 = await RetrievalDAO(async_session).create_retrieval(
        person_with_name_and_idref_db_model
    )
    retrieval_3 = await RetrievalDAO(async_session).create_retrieval(
        person_with_name_and_idref_db_model
    )
    return [retrieval_1, retrieval_2, retrieval_3]


@pytest_asyncio.fixture(name="retrieval_db_model_for_person_with_id_hal_i")
async def fixture_retrieval_db_model_for_person_with_id_hal_i(
    async_session, person_with_name_and_id_hal_i_db_model
) -> DbRetrieval:
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
) -> DbRetrieval:
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
) -> DbRetrieval:
    """
    Generate a retrieval with a person with first name, last name, ID_HAL_I and ID_HAL_S

    :param async_session: async db session
    :param person_with_name_and_id_hal_i_s_db_model: person  in DB model format
    :return: retrieval with a person with first name, last name and ID_HAL_I  ID_HAL_S
    """
    return await RetrievalDAO(async_session).create_retrieval(
        person_with_name_and_id_hal_i_s_db_model
    )
