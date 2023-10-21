"""Tests for entity dao."""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.daos.reference_dao import ReferenceDAO
from app.db.models.harvesting import Harvesting
from app.db.models.reference import Reference as DbReference
from app.db.models.reference_event import ReferenceEvent
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


@pytest.mark.asyncio
async def test_get_references_for_entity_and_harvester_only_returns_last_version(
    async_session: AsyncSession, harvesting_db_model: Harvesting
):
    """
    GIVEN two references in database with the same source identifier and successive version numbers
    WHEN get_references_for_entity_and_harvester is called with the source identifier
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
    reference_event_1 = ReferenceEvent(
        type=ReferenceEvent.Type.CREATED.value,
        reference=reference1,
        harvesting=harvesting_db_model,
        history=True,
    )
    reference_event_2 = ReferenceEvent(
        type=ReferenceEvent.Type.UPDATED.value,
        reference=reference2,
        harvesting=harvesting_db_model,
        history=True,
    )
    async_session.add_all(
        [reference1, reference2, reference_event_1, reference_event_2]
    )
    await async_session.commit()
    dao = ReferenceDAO(async_session)

    references = await dao.get_references_for_entity_and_harvester(
        harvester=harvester, entity_id=harvesting_db_model.retrieval.entity_id
    )

    assert references == [reference2]
    assert references[0].titles[0].value == "changed_title"


@pytest.mark.asyncio
async def test_get_references_for_entity_and_harvester_returns_last_version_even_if_deleted(
    async_session: AsyncSession, harvesting_db_model: Harvesting
):
    """
    GIVEN two references in database with the same source identifier and successive version numbers
            where the last one is deleted
    WHEN get_references_for_entity_and_harvester is called with the source identifier
    THEN the returned reference is the last one and is deleted
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
    reference_event_1 = ReferenceEvent(
        type=ReferenceEvent.Type.CREATED.value,
        reference=reference1,
        harvesting=harvesting_db_model,
        history=True,
    )
    reference_event_2 = ReferenceEvent(
        type=ReferenceEvent.Type.UPDATED.value,
        reference=reference2,
        harvesting=harvesting_db_model,
        history=True,
    )
    reference_event_3 = ReferenceEvent(
        type=ReferenceEvent.Type.DELETED.value,
        reference=reference2,
        harvesting=harvesting_db_model,
        history=True,
    )
    async_session.add_all(
        [
            reference1,
            reference2,
            reference_event_1,
            reference_event_2,
            reference_event_3,
        ]
    )
    await async_session.commit()
    dao = ReferenceDAO(async_session)

    references = await dao.get_references_for_entity_and_harvester(
        harvester=harvester, entity_id=harvesting_db_model.retrieval.entity_id
    )

    assert references == [reference2]
    assert references[0].titles[0].value == "changed_title"
    assert references[0].deleted
