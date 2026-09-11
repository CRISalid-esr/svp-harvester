"""Tests for idref harvester relevance."""
from unittest import mock

import pytest

from app.db.models.contributor_identifier import ContributorIdentifier
from app.db.models.person import Person as DbPerson
from app.harvesters.idref.idref_harvester import IdrefHarvester
from app.harvesters.idref.idref_references_converter import IdrefReferencesConverter


@pytest.mark.asyncio
async def test_idref_harvester_relevant_with_idref(
    person_with_name_and_idref_db_model: DbPerson,
):
    """Test that the harvester is relevant after set_entity_id selects an idref identifier."""
    harvester = IdrefHarvester(converter=IdrefReferencesConverter(name="idref"))
    with mock.patch.object(
        IdrefHarvester, "_get_entity", new=mock.AsyncMock(
            return_value=person_with_name_and_idref_db_model
        )
    ):
        await harvester.set_entity_id(1)
    assert harvester.is_relevant() is True
    assert harvester.entity_identifier_used[0] == (
        ContributorIdentifier.IdentifierType.IDREF.value
    )


@pytest.mark.asyncio
async def test_idref_harvester_relevant_with_orcid(
    person_with_name_and_orcid_db_model: DbPerson,
):
    """Test that the harvester is relevant after set_entity_id selects an orcid identifier."""
    harvester = IdrefHarvester(converter=IdrefReferencesConverter(name="idref"))
    with mock.patch.object(
        IdrefHarvester, "_get_entity", new=mock.AsyncMock(
            return_value=person_with_name_and_orcid_db_model
        )
    ):
        await harvester.set_entity_id(1)
    assert harvester.is_relevant() is True
    assert harvester.entity_identifier_used[0] == (
        ContributorIdentifier.IdentifierType.ORCID.value
    )
