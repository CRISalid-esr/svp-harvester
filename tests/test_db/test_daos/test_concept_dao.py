import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.daos.concept_dao import ConceptDAO
from app.db.models.concept import Concept


@pytest.mark.asyncio
async def test_random_concept_not_derefenced(async_session: AsyncSession):
    """
    Test that we can get a random concept that has not been dereferenced yet.
    :param async_session: async session fixture
    :return: None
    """
    concept = Concept(uri="http://example.com/concept", dereferenced=False)
    async_session.add(concept)
    await async_session.commit()

    dao = ConceptDAO(async_session)
    concept_from_db = await dao.get_random_concept_not_dereferenced()

    assert concept_from_db is not None
    assert isinstance(concept_from_db, Concept)
    assert concept_from_db.uri == "http://example.com/concept"


@pytest.mark.asyncio
async def test_random_concept_already_derenfenced(async_session: AsyncSession):
    """
    Test that if there are no concepts to dereference, the method returns None.
    """
    concept = Concept(uri="http://example.com/concept", dereferenced=True)
    async_session.add(concept)
    await async_session.commit()

    dao = ConceptDAO(async_session)
    concept_from_db = await dao.get_random_concept_not_dereferenced()

    assert concept_from_db is None


@pytest.mark.asyncio
async def test_random_concept_with_exclude_id(async_session: AsyncSession):
    """
    Test that if we provide a list of ids to exclude, the method does not return
    any of these concepts.
    """
    concept1 = Concept(uri="http://example.com/concept1", dereferenced=False)
    concept2 = Concept(uri="http://example.com/concept2", dereferenced=False)
    async_session.add(concept1)
    async_session.add(concept2)
    await async_session.commit()

    dao = ConceptDAO(async_session)
    concept_from_db = await dao.get_random_concept_not_dereferenced(
        exclude_ids=[concept1.id]
    )

    assert concept_from_db is not None
    assert concept_from_db.uri == "http://example.com/concept2"

    concept_from_db = await dao.get_random_concept_not_dereferenced(
        exclude_ids=[concept1.id, concept2.id]
    )

    assert concept_from_db is None
