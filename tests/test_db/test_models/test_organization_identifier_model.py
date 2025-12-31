import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.organization import Organization
from app.db.models.organization_identifier import OrganizationIdentifier


@pytest.mark.asyncio
async def test_organization_identifier_rejects_unknown_type(
    async_session: AsyncSession,
):
    """
    GIVEN an OrganizationIdentifier with an unsupported type
    WHEN it is created / persisted
    THEN a ValueError is raised by the validator
    """
    org = Organization(
        source="scanr",
        source_identifier="x",
        name="Test org",
        type=None,
    )

    with pytest.raises(ValueError, match="not supported"):
        org.identifiers.append(OrganizationIdentifier(type="unknown_type", value="abc"))


@pytest.mark.asyncio
async def test_organization_identifier_normalizes_ror_url(async_session: AsyncSession):
    """
    GIVEN a ROR identifier with a full URL
    WHEN it is persisted
    THEN value is normalized (domain stripped)
    """
    org = Organization(
        source="scanr", source_identifier="x", name="Test org", type=None
    )
    ident = OrganizationIdentifier(type="ror", value="https://ror.org/00aycez97")
    org.identifiers.append(ident)

    async_session.add(org)
    await async_session.commit()
    await async_session.refresh(org)

    assert org.identifiers[0].value == "00aycez97"


@pytest.mark.asyncio
async def test_organization_identifier_normalizes_idref_url_and_trailing_id(
    async_session: AsyncSession,
):
    """
    GIVEN an IDREF identifier with URL + trailing '/id'
    WHEN it is persisted
    THEN value is normalized
    """
    org = Organization(
        source="scanr", source_identifier="x", name="Test org", type=None
    )
    ident = OrganizationIdentifier(
        type="idref", value="https://www.idref.fr/123456789/id"
    )
    org.identifiers.append(ident)

    async_session.add(org)
    await async_session.commit()
    await async_session.refresh(org)

    assert org.identifiers[0].value == "123456789"


@pytest.mark.asyncio
async def test_organization_identifier_keeps_value_for_non_normalized_types(
    async_session: AsyncSession,
):
    """
    GIVEN a type without normalization rule (e.g. hal)
    WHEN it is persisted
    THEN value remains unchanged
    """
    org = Organization(
        source="scanr", source_identifier="x", name="Test org", type=None
    )
    ident = OrganizationIdentifier(type="hal", value="http://example.org/not-stripped")
    org.identifiers.append(ident)

    async_session.add(org)
    await async_session.commit()
    await async_session.refresh(org)

    assert org.identifiers[0].value == "http://example.org/not-stripped"


@pytest.mark.asyncio
async def test_organization_identifier_persists_extra_information_jsonb(
    async_session: AsyncSession,
):
    """
    GIVEN an OrganizationIdentifier with extra_information
    WHEN persisted and reloaded
    THEN extra_information is preserved
    """
    payload = {
        "types": ["facility"],
        "status": "active",
        "established": 1995,
        "geonames_locations": [
            {
                "geonames_id": 2992166,
                "continent_code": "EU",
                "continent_name": "Europe",
                "country_code": "FR",
                "country_name": "France",
                "lat": 43.61093,
                "lng": 3.87635,
                "name": "Montpellier",
            }
        ],
    }

    org = Organization(
        source="scanr", source_identifier="x", name="Test org", type=None
    )
    ident = OrganizationIdentifier(
        type="ror",
        value="00aycez97",
        extra_information=payload,
    )
    org.identifiers.append(ident)

    async_session.add(org)
    await async_session.commit()
    async_session.expunge_all()

    org2 = await async_session.get(Organization, org.id)
    assert org2 is not None
    assert len(org2.identifiers) == 1
    assert org2.identifiers[0].extra_information == payload
