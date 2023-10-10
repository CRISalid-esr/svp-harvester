"""Tests for the retrieval dao."""
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.daos.retrieval_dao import RetrievalDAO
from app.db.models.identifier_model import Identifier as DbIdentifier
from app.db.models.person_model import Person as DbPerson
from app.db.models.retrieval_model import Retrieval as DbRetrieval


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
    stmt = select(DbRetrieval).join(DbPerson).where(DbPerson.name == "John Doe")
    retrieval_from_db = (await async_session.execute(stmt)).unique().scalar_one()
    assert retrieval_from_db.entity.name == "John Doe"
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
    stmt = select(DbRetrieval).join(DbPerson).where(DbPerson.name == "John Doe")
    created_retrieval = (await async_session.execute(stmt)).unique().scalar_one()
    retrieval_id = created_retrieval.id
    retrieval_from_db = await dao.get_retrieval_by_id(retrieval_id)
    assert retrieval_from_db.entity.name == "John Doe"
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
    assert person_from_db.name == "John Doe"
    assert len(person_from_db.identifiers) == 1
    assert person_from_db.identifiers[0].type == "idref"
    assert person_from_db.identifiers[0].value == "123456789"
