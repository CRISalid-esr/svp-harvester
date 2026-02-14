"""Tests for Organization.ensure_self_identifier()."""

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.db.models.organization import Organization
from app.db.models.organization_identifier import OrganizationIdentifier


@pytest.mark.asyncio
async def test_ensure_self_identifier_adds_hal_identifier(async_session: AsyncSession):
    """
    GIVEN an Organization with source="hal"
    WHEN ensure_self_identifier() is called and the org is persisted
    THEN the org has at least one identifier (type="hal", value=source_identifier)
    """
    org = Organization(
        source="hal",
        source_identifier="12345",
        name="Test HAL Org",
        type="laboratory",
    )

    org.ensure_self_identifier()

    async_session.add(org)
    await async_session.commit()
    async_session.expunge_all()

    stmt = (
        select(Organization)
        .options(joinedload(Organization.identifiers))
        .where(Organization.source == "hal")
        .where(Organization.source_identifier == "12345")
    )
    org_from_db = (await async_session.execute(stmt)).unique().scalars().one()

    assert org_from_db is not None
    assert any(
        ident.type == OrganizationIdentifier.IdentifierType.HAL.value
        and ident.value == "12345"
        for ident in org_from_db.identifiers
    )


@pytest.mark.asyncio
async def test_ensure_self_identifier_does_not_duplicate_manual_self_identifier(
    async_session: AsyncSession,
):
    """
    GIVEN an Organization for which the self-identifier was added manually
    WHEN ensure_self_identifier() is called
    THEN it does not create a duplicate self-identifier.
    """
    org = Organization(
        source="hal",
        source_identifier="777",
        name="Manual HAL Org",
        type="laboratory",
    )

    # Manually add the expected self identifier
    org.identifiers.append(
        OrganizationIdentifier(
            type=OrganizationIdentifier.IdentifierType.HAL.value, value="777"
        )
    )

    # Ensure should be idempotent and not add a duplicate
    org.ensure_self_identifier()

    async_session.add(org)
    await async_session.commit()
    async_session.expunge_all()

    stmt = (
        select(Organization)
        .options(joinedload(Organization.identifiers))
        .where(Organization.source == "hal")
        .where(Organization.source_identifier == "777")
    )
    org_from_db = (await async_session.execute(stmt)).unique().scalars().one()

    matches = [
        ident
        for ident in org_from_db.identifiers
        if ident.type == OrganizationIdentifier.IdentifierType.HAL.value
        and ident.value == "777"
    ]
    assert len(matches) == 1


@pytest.mark.asyncio
async def test_ensure_self_identifier_adds_openalex_identifier(
    async_session: AsyncSession,
):
    """
    GIVEN an Organization with source='openalex'
    WHEN ensure_self_identifier() is called and the org is persisted
    THEN the org has at least one identifier (type='openalex', value=source_identifier)
    """
    org = Organization(
        source="openalex",
        source_identifier="OA:ABCDEF",
        name="Test OpenAlex Org",
        type="institution",
    )

    org.ensure_self_identifier()

    async_session.add(org)
    await async_session.commit()
    async_session.expunge_all()

    stmt = (
        select(Organization)
        .options(joinedload(Organization.identifiers))
        .where(Organization.source == "openalex")
        .where(Organization.source_identifier == "OA:ABCDEF")
    )
    org_from_db = (await async_session.execute(stmt)).unique().scalars().one()

    assert any(
        ident.type == OrganizationIdentifier.IdentifierType.OPEN_ALEX.value
        and ident.value == "OA:ABCDEF"
        for ident in org_from_db.identifiers
    )


@pytest.mark.asyncio
async def test_ensure_self_identifier_is_idempotent(async_session: AsyncSession):
    """
    GIVEN an Organization with source="hal"
    WHEN ensure_self_identifier() is called multiple times
    THEN it does not create duplicate self-identifiers.
    """
    org = Organization(
        source="hal",
        source_identifier="999",
        name="Idempotent HAL Org",
        type="laboratory",
    )

    org.ensure_self_identifier()
    org.ensure_self_identifier()

    async_session.add(org)
    await async_session.commit()
    async_session.expunge_all()

    stmt = (
        select(Organization)
        .options(joinedload(Organization.identifiers))
        .where(Organization.source == "hal")
        .where(Organization.source_identifier == "999")
    )
    org_from_db = (await async_session.execute(stmt)).unique().scalars().one()

    matches = [
        ident
        for ident in org_from_db.identifiers
        if ident.type == OrganizationIdentifier.IdentifierType.HAL.value
        and ident.value == "999"
    ]
    assert len(matches) == 1


@pytest.mark.asyncio
async def test_ensure_self_identifier_does_nothing_for_other_sources(
    async_session: AsyncSession,
):
    """
    GIVEN an Organization with a source not requiring a self identifier
    WHEN ensure_self_identifier() is called
    THEN it does not add a (type==source, value==source_identifier) identifier.
    """
    org = Organization(
        source="scanr",
        source_identifier="scanr:1",
        name="SCANR Org",
        type="institution",
    )

    org.ensure_self_identifier()

    async_session.add(org)
    await async_session.commit()
    async_session.expunge_all()

    stmt = (
        select(Organization)
        .options(joinedload(Organization.identifiers))
        .where(Organization.source == "scanr")
        .where(Organization.source_identifier == "scanr:1")
    )
    org_from_db = (await async_session.execute(stmt)).unique().scalars().one()

    assert not any(
        ident.value == "scanr:1" for ident in (org_from_db.identifiers or [])
    )
