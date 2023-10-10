"""Tests for entity dao."""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.daos.entity_dao import EntityDAO
from app.db.models.person_model import Person as DbPerson


@pytest.mark.asyncio
async def test_get_entity_by_id(async_session: AsyncSession):
    """
    Test that we can get an entity by its id.
    :param async_session: async session fixture
    :return: None
    """
    person = DbPerson(name="John Doe")
    async_session.add(person)
    await async_session.commit()
    dao = EntityDAO(async_session)
    entity_from_db = await dao.get_entity_by_id(person.id)
    assert isinstance(entity_from_db, DbPerson)
    assert entity_from_db.name == "John Doe"
