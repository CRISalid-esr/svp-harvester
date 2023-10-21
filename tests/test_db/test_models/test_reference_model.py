"""Tests for the Person model."""
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.reference import Reference
from app.db.models.reference_event import ReferenceEvent
from app.db.models.title import Title


@pytest.mark.asyncio
async def test_orphan_titles_deletion(async_session: AsyncSession):
    """
    GIVEN a reference with a title
    WHEN the reference is deleted
    THEN the title is deleted
    """
    title = Title(value="title", language="fr")
    reference = Reference(
        source_identifier="source_identifier_1234",
        harvester="harvester",
        hash="hash",
        version=0,
        titles=[title],
    )
    async_session.add(reference)
    await async_session.commit()
    title_id = title.id
    await async_session.delete(reference)
    await async_session.commit()
    query = select(Title).where(Title.id == title_id)
    title: Title = (await async_session.execute(query)).scalar()
    assert title is None


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "event_type, history, expected_deleted",
    [
        (ReferenceEvent.Type.DELETED, True, True),
        (ReferenceEvent.Type.DELETED, False, False),
        (ReferenceEvent.Type.CREATED, True, False),
        (ReferenceEvent.Type.CREATED, False, False),
        (ReferenceEvent.Type.UPDATED, True, False),
        (ReferenceEvent.Type.UPDATED, False, False),
    ],
)
async def test__reference_marked_as_deleted(
    async_session: AsyncSession,
    harvesting_db_model: "app.db.models.harvesting.Harvesting",
    event_type: ReferenceEvent.Type,
    history: bool,
    expected_deleted: bool,
):
    """
    GIVEN a reference
    WHEN a reference_event is added to it with type deleted
    THEN the reference is marked as deleted
    """
    reference = Reference(
        source_identifier="source_identifier_1234",
        harvester="harvester",
        hash="hash",
        version=0,
    )
    async_session.add(reference)
    await async_session.commit()
    assert reference.deleted is False
    reference_event = ReferenceEvent(
        type=event_type.value,
        reference=reference,
        harvesting_id=harvesting_db_model.id,
        history=history,
    )
    async_session.add(reference_event)
    await async_session.commit()
    query = select(Reference).where(Reference.id == reference.id)
    reference: Reference = (await async_session.execute(query)).scalar()
    assert reference.deleted is expected_deleted
