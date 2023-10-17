"""Tests for the harvesting dao."""
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.daos.harvesting_dao import HarvestingDAO
from app.db.models.harvesting import Harvesting
from app.db.models.retrieval import Retrieval as DbRetrieval


@pytest.mark.asyncio
async def test_create_harvesting(async_session: AsyncSession, retrieval_db_model):
    """
    Test that we can create a harvesting for a retrieval in the database.
    :param async_session: async session fixture
    :param retrieval_db_model: retrieval fixture
    :return: None
    """
    dao = HarvestingDAO(async_session)
    await dao.create_harvesting(
        retrieval_db_model, "idref", state=Harvesting.State.RUNNING
    )
    await async_session.commit()
    stmt = (
        select(Harvesting)
        .join(Harvesting.retrieval)
        .where(DbRetrieval.id == retrieval_db_model.id)
    )
    harvesting_from_db = (await async_session.execute(stmt)).unique().scalar_one()
    assert harvesting_from_db.harvester == "idref"


@pytest.mark.asyncio
async def test_update_harvesting_state(async_session: AsyncSession, retrieval_db_model):
    """
    Test that we can create a harvesting for a retrieval in the database.
    :param async_session: async session fixture
    :param retrieval_db_model: retrieval fixture
    :return: None
    """
    dao = HarvestingDAO(async_session)
    harvesting = await dao.create_harvesting(
        retrieval_db_model, "idref", state=Harvesting.State.RUNNING
    )
    await async_session.commit()
    await dao.update_harvesting_state(harvesting.id, Harvesting.State.COMPLETED)
    harvesting_from_db = await dao.get_harvesting_by_id(harvesting.id)
    assert harvesting_from_db.state == Harvesting.State.COMPLETED.value
