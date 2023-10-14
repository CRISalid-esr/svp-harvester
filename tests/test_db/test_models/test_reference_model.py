"""Tests for the Person model."""
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.reference import Reference
from app.db.models.title import Title


@pytest.mark.asyncio
async def test_titles_cascade_deletion(async_session: AsyncSession):
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
