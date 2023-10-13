"""Tests for entity dao."""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.daos.reference_dao import ReferenceDAO
from app.db.models.harvesting import Harvesting
from app.db.models.reference import Reference as DbReference
from app.db.models.title import Title


@pytest.mark.asyncio
async def test_get_references_by_source_identifier(
    async_session: AsyncSession, harvesting_db_model: Harvesting
):
    """
    GIVEN two references in database with the same source identifier and successive version numbers
    WHEN get_references_by_source_identifier is called with the source identifier
    THEN the references are returned
    """
    harvester = harvesting_db_model.harvester
    source_identifier = "source_identifier_1234"
    reference1 = DbReference(
        source_identifier=source_identifier,
        harvester=harvester,
        hash="hash1",
        version=0,
        titles=[Title(value="title", language="fr")],
    )
    reference2 = DbReference(
        source_identifier=source_identifier,
        harvester=harvester,
        hash="hash2",
        version=1,
        titles=[Title(value="changed_title", language="fr")],
    )
    async_session.add_all([reference1, reference2])
    await async_session.commit()
    dao = ReferenceDAO(async_session)

    references = await dao.get_references_by_source_identifier(
        harvester=harvester, source_identifier=source_identifier
    )

    assert references == [reference1, reference2]


@pytest.mark.asyncio
async def test_get_last_reference_by_source_identifier(
    async_session: AsyncSession, harvesting_db_model
):
    """
    GIVEN two references in database with the same source identifier and successive version numbers
    WHEN get_last_reference_by_source_identifier is called with the source identifier
    THEN the last reference is returned
    """
    harvester = harvesting_db_model.harvester
    source_identifier = "source_identifier_1234"
    reference1 = DbReference(
        source_identifier=source_identifier,
        harvester=harvester,
        hash="hash1",
        version=0,
        titles=[Title(value="title", language="fr")],
    )
    reference2 = DbReference(
        source_identifier=source_identifier,
        harvester=harvester,
        hash="hash2",
        version=1,
        titles=[Title(value="changed_title", language="fr")],
    )
    async_session.add_all([reference1, reference2])
    await async_session.commit()
    dao = ReferenceDAO(async_session)

    reference = await dao.get_last_reference_by_source_identifier(
        harvester=harvester, source_identifier=source_identifier
    )

    assert reference == reference2
    assert reference.titles[0].value == "changed_title"
