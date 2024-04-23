"""Tests for the Person model."""

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.db.models.contribution import Contribution
from app.db.models.contributor import Contributor
from app.db.models.organization import Organization
from app.db.models.reference import Reference
from app.db.models.title import Title


@pytest.mark.asyncio
async def test_contributor(async_session: AsyncSession):
    """
    GIVEN a reference with a contributor
    WHEN the reference is committed to the database
    THEN ask the contributor from the database and check that it owns the reference.
    """
    contributor = Contributor(
        source="hal",
        source_identifier="source_identifier_1234",
        name="John Doe",
    )

    reference = Reference(
        source_identifier="source_identifier_1234",
        harvester="harvester",
        hash="hash",
        version=0,
        titles=[Title(value="title", language="fr")],
        contributions=[
            Contribution(role=Contribution.get_url("ILL"), contributor=contributor)
        ],
    )
    async_session.add(reference)
    await async_session.commit()
    async_session.expunge_all()
    # find the contributor by source and source identifier
    stmt = (
        select(Contributor)
        .options(
            joinedload(Contributor.contributions)
            .joinedload(Contribution.reference)
            .joinedload(Reference.contributions)
        )
        .where(Contributor.source == "hal")
        .where(Contributor.source_identifier == "source_identifier_1234")
    )
    contributor_from_db = (await async_session.execute(stmt)).unique().scalars().one()
    assert contributor_from_db is not None
    assert contributor_from_db.name == "John Doe"
    assert len(contributor_from_db.contributions) == 1
    assert contributor_from_db.contributions[0].role == Contribution.get_url("ILL")
    reference = contributor_from_db.contributions[0].reference
    assert reference.source_identifier == "source_identifier_1234"
    assert reference.harvester == "harvester"
    assert reference.hash == "hash"
    assert reference.version == 0
    assert len(reference.titles) == 1
    assert reference.titles[0].value == "title"
    assert reference.titles[0].language == "fr"
    assert len(reference.contributions) == 1


@pytest.mark.asyncio
async def test_contributor_with_organisation(async_session: AsyncSession):
    """
    GIVEN a reference with a contributor with an organisation
    WHEN the reference is committed to the database
    THEN ask the organisation from the database and check that it owns the reference.
    """
    organization = Organization(
        source="hal",
        source_identifier="source_identifier_1234",
        name="Physics Department",
        type="laboratory",
    )

    contributor = Contributor(
        source="hal", source_identifier="source_identifier_1234", name="John Doe"
    )

    reference = Reference(
        source_identifier="source_identifier_1234",
        harvester="harvester",
        hash="hash",
        version=0,
        titles=[Title(value="title", language="fr")],
        contributions=[
            Contribution(
                role=Contribution.get_url("ILL"),
                contributor=contributor,
                affiliations=[organization],
            )
        ],
    )
    async_session.add(reference)
    await async_session.commit()
    async_session.expunge_all()
    # find the contributor by source and source identifier
    stmt = (
        select(Organization)
        .options(
            joinedload(Organization.contributions).joinedload(Contribution.reference)
        )
        .where(Organization.source == "hal")
        .where(Organization.source_identifier == "source_identifier_1234")
    )
    organization_from_db = (await async_session.execute(stmt)).unique().scalars().one()
    assert organization_from_db is not None
    assert organization_from_db.name == "Physics Department"
    assert len(organization_from_db.contributions) == 1
    assert organization_from_db.contributions[0].role == Contribution.get_url("ILL")
    reference = organization_from_db.contributions[0].reference
    assert reference.source_identifier == "source_identifier_1234"
    assert reference.harvester == "harvester"
    assert reference.hash == "hash"
    assert reference.version == 0


def test_validate_role():
    # Test with a valid role_uri
    valid_role_uri = Contribution.LOCAuthorRoles.AUT.loc_url()
    contribution = Contribution(role=valid_role_uri)
    assert contribution.role == valid_role_uri

    # Test with an invalid role_uri
    invalid_role_uri = "invalid_uri"
    with pytest.raises(ValueError):
        Contribution(role=invalid_role_uri)
