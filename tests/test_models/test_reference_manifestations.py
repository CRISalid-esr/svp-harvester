"""Tests for the ReferenceManifestation model."""

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.reference_manifestation import ReferenceManifestation


def test_manifestation_with_invalid_url():
    """
    GIVEN a syntactically invalid URL
    WHEN the manifestation is created
    THEN check a validation error is raised
    """
    with pytest.raises(
        ValueError,
        match="Page URL http:// is not a valid URL",
    ):
        ReferenceManifestation(page="http://", download_url="http://example.com")


def test_manifestation_with_valid_url():
    """
    GIVEN a syntactically valid URL
    WHEN the manifestation is created
    THEN check the manifestation is created
    """
    manifestation = ReferenceManifestation(
        page="http://example.com", download_url="http://example.com"
    )
    assert manifestation.page == "http://example.com"
    assert manifestation.download_url == "http://example.com"


async def test_manifestation_without_page_fails(async_session: AsyncSession):
    """
    GIVEN a manifestation without a page
    WHEN the manifestation is created
    THEN check a validation error is raised
    """
    manifestation = ReferenceManifestation(download_url="http://example.com")
    async_session.add(manifestation)
    with pytest.raises(IntegrityError):
        await async_session.commit()
