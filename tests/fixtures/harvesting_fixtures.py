from typing import List

import pytest_asyncio

from app.db.daos.harvesting_dao import HarvestingDAO
from app.db.models.harvesting import Harvesting as DbHarvesting


@pytest_asyncio.fixture(name="harvesting_db_model")
async def fixture_harvesting_db_model(
    async_session, retrieval_db_model
) -> DbHarvesting:
    """
    Generate a harvesting with a retrieval in DB model format

    :param async_session: async db session
    :param retrieval_db_model: retrieval in DB model format
    :return:  harvesting in DB model format
    """
    return await HarvestingDAO(async_session).create_harvesting(
        retrieval_db_model, "idref", DbHarvesting.State.RUNNING
    )


@pytest_asyncio.fixture(name="two_completed_harvestings_db_models_for_same_person")
async def fixture_two_completed_harvestings_db_models_for_same_person(
    async_session, two_retrievals_db_models_for_same_person
) -> List[DbHarvesting]:
    """
    Generate two harvestings with a retrieval in DB model format

    :param async_session: async db session
    :param two_retrievals_db_models_for_same_person: two retrievals in DB model format
            for same person with same identifiers
    :return: two harvestings with a retrieval in DB model format
    """
    harvesting_1 = await HarvestingDAO(async_session).create_harvesting(
        two_retrievals_db_models_for_same_person[0],
        "idref",
        DbHarvesting.State.COMPLETED,
    )
    harvesting_2 = await HarvestingDAO(async_session).create_harvesting(
        two_retrievals_db_models_for_same_person[1],
        "idref",
        DbHarvesting.State.COMPLETED,
    )
    return [harvesting_1, harvesting_2]


@pytest_asyncio.fixture(name="three_completed_harvestings_db_models_for_same_person")
async def fixture_three_completed_harvestings_db_models_for_same_person(
    async_session, three_retrievals_db_models_for_same_person
) -> List[DbHarvesting]:
    """
    Generate three harvestings with a retrieval in DB model format

    :param async_session: async db session
    :param three_retrievals_db_models_for_same_person: three retrievals in DB model format
            for same person with same identifiers
    :return: three harvestings with a retrieval in DB model format
    """
    harvesting_1 = await HarvestingDAO(async_session).create_harvesting(
        three_retrievals_db_models_for_same_person[0],
        "idref",
        DbHarvesting.State.COMPLETED,
    )
    harvesting_2 = await HarvestingDAO(async_session).create_harvesting(
        three_retrievals_db_models_for_same_person[1],
        "idref",
        DbHarvesting.State.COMPLETED,
    )
    harvesting_3 = await HarvestingDAO(async_session).create_harvesting(
        three_retrievals_db_models_for_same_person[2],
        "idref",
        DbHarvesting.State.COMPLETED,
    )
    return [harvesting_1, harvesting_2, harvesting_3]


@pytest_asyncio.fixture(name="hal_harvesting_db_model_id_hal_i")
async def fixture_hal_harvesting_db_model_id_hal_i(
    async_session, retrieval_db_model_for_person_with_id_hal_i
) -> DbHarvesting:
    """
    Generate a Hal harvesting with a retrieval in DB model format for person with ID_HAL_I

    :param async_session: async db session
    :param retrieval_db_model_for_person_with_id_hal_i: retrieval in DB model format
    :return:  Hal harvesting in DB model format
    """
    return await HarvestingDAO(async_session).create_harvesting(
        retrieval_db_model_for_person_with_id_hal_i, "hal", DbHarvesting.State.RUNNING
    )


@pytest_asyncio.fixture(name="hal_harvesting_db_model_id_hal_s")
async def fixture_hal_harvesting_db_model_id_hal_s(
    async_session, retrieval_db_model_for_person_with_id_hal_s
) -> DbHarvesting:
    """
    Generate a Hal harvesting with a retrieval in DB model format for person with ID_HAL_S

    :param async_session: async db session
    :param retrieval_db_model_for_person_with_id_hal_s: retrieval in DB model format
    :return:  Hal harvesting in DB model format
    """
    return await HarvestingDAO(async_session).create_harvesting(
        retrieval_db_model_for_person_with_id_hal_s, "hal", DbHarvesting.State.RUNNING
    )


@pytest_asyncio.fixture(name="hal_harvesting_db_model_id_hal_i_s")
async def fixture_hal_harvesting_db_model_id_hal_i_s(
    async_session, retrieval_db_model_for_person_with_id_hal_i_s
) -> DbHarvesting:
    """
    Generate a Hal harvesting with a retrieval in DB model format for person with ID_HAL_I

    :param async_session: async db session
    :param retrieval_db_model_for_person_with_id_hal_i_s: retrieval in DB model format
    :return:  Hal harvesting in DB model format
    """
    return await HarvestingDAO(async_session).create_harvesting(
        retrieval_db_model_for_person_with_id_hal_i_s, "hal", DbHarvesting.State.RUNNING
    )
