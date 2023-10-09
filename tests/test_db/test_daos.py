"""Tests for the Person model."""
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.daos import RetrievalDAO, HarvestingDAO, EntityDAO
from app.db.models.person_model import Person as DbPerson

from app.db.models.identifier_model import Identifier as DbIdentifier
from app.db.models.retrieval_model import Retrieval as DbRetrieval
from app.db.models.harvesting_model import Harvesting


@pytest.mark.asyncio
async def test_create_retrieval(
    async_session: AsyncSession, person_with_name_and_idref_db_model
):
    """
    Test that we can create a retrieval for a person in the database.
    :param async_session:  async session fixture
    :param person_with_name_and_idref_db_model:  person with name and idref fixture
    :return: None
    """
    dao = RetrievalDAO(async_session)
    await dao.create_retrieval(person_with_name_and_idref_db_model)
    stmt = select(DbRetrieval).join(DbPerson).where(DbPerson.first_name == "John")
    retrieval_from_db = (await async_session.execute(stmt)).unique().scalar_one()
    assert retrieval_from_db.entity.first_name == "John"
    assert retrieval_from_db.entity.last_name == "Doe"
    assert len(retrieval_from_db.entity.identifiers) == 1


@pytest.mark.asyncio
async def test_get_retrieval(
    async_session: AsyncSession, person_with_name_and_idref_db_model
):
    """
    Test that we can get a retrieval by its id.
    :param async_session: async session fixture
    :param person_with_name_and_idref_db_model: person with name and idref fixture
    :return: None
    """
    dao = RetrievalDAO(async_session)
    await dao.create_retrieval(person_with_name_and_idref_db_model)
    stmt = select(DbRetrieval).join(DbPerson).where(DbPerson.first_name == "John")
    created_retrieval = (await async_session.execute(stmt)).unique().scalar_one()
    retrieval_id = created_retrieval.id
    retrieval_from_db = await dao.get_retrieval_by_id(retrieval_id)
    assert retrieval_from_db.entity.first_name == "John"
    assert retrieval_from_db.entity.last_name == "Doe"
    assert len(retrieval_from_db.entity.identifiers) == 1


@pytest.mark.asyncio
async def test_create_retrieval_registers_person(
    async_session: AsyncSession, person_with_name_and_idref_db_model
):
    """
    Test that creating a retrieval registers the person in the database
    :param async_session: async session fixture
    :param person_with_name_and_idref_db_model:   person with name and idref fixture
    :return: None
    """
    dao = RetrievalDAO(async_session)
    await dao.create_retrieval(person_with_name_and_idref_db_model)
    stmt = (
        select(DbPerson)
        .join(DbPerson.identifiers)
        .where(DbIdentifier.value == "123456789")
    )
    person_from_db = (await async_session.execute(stmt)).unique().scalar_one()
    assert person_from_db.first_name == "John"
    assert len(person_from_db.identifiers) == 1
    assert person_from_db.identifiers[0].type == "idref"
    assert person_from_db.identifiers[0].value == "123456789"


@pytest.mark.asyncio
async def test_create_harvesting(async_session: AsyncSession, retrieval_db_model):
    """
    Test that we can create a harvesting for a retrieval in the database.
    :param async_session: async session fixture
    :param retrieval_db_model: retrieval fixture
    :return: None
    """
    dao = HarvestingDAO(async_session)
    await dao.create_harvesting(retrieval_db_model, "idref", state=Harvesting.State.RUNNING)
    await async_session.commit()
    stmt = (
        select(Harvesting)
        .join(Harvesting.retrieval)
        .where(DbRetrieval.id == retrieval_db_model.id)
    )
    harvesting_from_db = (await async_session.execute(stmt)).scalar_one()
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


@pytest.mark.asyncio
async def test_get_entity_by_id(async_session: AsyncSession):
    """
    Test that we can get an entity by its id.
    :param async_session: async session fixture
    :return: None
    """
    person = DbPerson(first_name="John", last_name="Doe")
    async_session.add(person)
    await async_session.commit()
    dao = EntityDAO(async_session)
    entity_from_db = await dao.get_entity_by_id(person.id)
    assert isinstance(entity_from_db, DbPerson)
    assert entity_from_db.first_name == "John"
    assert entity_from_db.last_name == "Doe"
