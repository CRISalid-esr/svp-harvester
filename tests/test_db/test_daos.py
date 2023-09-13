"""Tests for the Person model."""
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.daos import RetrievalDAO, HarvestingDAO
from app.db.models import (
    Person as DbPerson,
    Identifier as DbIdentifier,
    Retrieval as DbRetrieval, Harvesting,
)
from app.models.identifiers import IdentifierTypeEnum


@pytest.mark.asyncio
async def test_create_retrieval(
    async_session: AsyncSession, person_with_name_and_idref_db_model
):
    dao = RetrievalDAO(async_session)
    retrieval = await dao.create_retrieval(person_with_name_and_idref_db_model)
    stmt = select(DbRetrieval).join(DbPerson).where(DbPerson.first_name == "John")
    retrieval_from_db = (await async_session.execute(stmt)).scalar_one()
    assert retrieval_from_db.entity.first_name == "John"
    assert retrieval_from_db.entity.last_name == "Doe"
    assert len(retrieval_from_db.entity.identifiers) == 1

@pytest.mark.asyncio
async def test_get_retrieval(
    async_session: AsyncSession, person_with_name_and_idref_db_model
):
    dao = RetrievalDAO(async_session)
    retrieval = await dao.create_retrieval(person_with_name_and_idref_db_model)
    stmt = select(DbRetrieval).join(DbPerson).where(DbPerson.first_name == "John")
    created_retrieval = (await async_session.execute(stmt)).scalar_one()
    retrieval_id = created_retrieval.id
    retrieval_from_db = await dao.get_retrieval_by_id(retrieval_id)
    assert retrieval_from_db.entity.first_name == "John"
    assert retrieval_from_db.entity.last_name == "Doe"
    assert len(retrieval_from_db.entity.identifiers) == 1

@pytest.mark.asyncio
async def test_create_retrieval_registers_person(
    async_session: AsyncSession, person_with_name_and_idref_db_model
):
    dao = RetrievalDAO(async_session)
    retrieval = await dao.create_retrieval(person_with_name_and_idref_db_model)
    stmt = (
        select(DbPerson)
        .join(DbPerson.identifiers)
        .where(DbIdentifier.value == "123456789")
    )
    person_from_db = (await async_session.execute(stmt)).scalar_one()
    assert person_from_db.first_name == "John"
    assert len(person_from_db.identifiers) == 1
    assert person_from_db.identifiers[0].type == IdentifierTypeEnum.IDREF
    assert person_from_db.identifiers[0].value == "123456789"

@pytest.mark.asyncio
async def test_create_harvesting(
    async_session: AsyncSession, retrieval_db_model
):
    dao = HarvestingDAO(async_session)
    await dao.create_harvesting(retrieval_db_model, "idref")
    stmt = (
        select(Harvesting)
        .join(Harvesting.retrieval)
        .where(DbRetrieval.id == retrieval_db_model.id)
    )
    harvesting_from_db = (await async_session.execute(stmt)).scalar_one()
    assert harvesting_from_db.harvester == "idref"