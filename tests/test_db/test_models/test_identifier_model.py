"""Tests for the Person model."""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.identifier_model import (
    Identifier as DbIdentifier,
)


@pytest.mark.asyncio
async def test_person_cannot_have_same_identifier_twice(
    async_session: AsyncSession, person_with_name_and_idref_db_model
):
    """
    GIVEN a person with an Idref identifier
    WHEN another identifier with the same type is added
    THEN check a validation error is raised
    """
    with pytest.raises(
        ValueError, match="Identifier of type idref already present for"
    ):
        person_with_name_and_idref_db_model.identifiers.append(
            DbIdentifier(type="idref", value="123456789")
        )
        async_session.add(person_with_name_and_idref_db_model)


@pytest.mark.asyncio
async def test_person_cannot_be_given_identifier_of_unknown_type(
    async_session: AsyncSession, person_with_name_and_idref_db_model
):
    """
    GIVEN a person with an identifier of any type
    WHEN another identifier with an unknown type is added
    THEN check a validation error is raised
    """
    with pytest.raises(
        ValueError, match="Identifier type is not referenced by settings"
    ):
        person_with_name_and_idref_db_model.identifiers.append(
            DbIdentifier(type="unknown", value="123456789")
        )
        async_session.add(person_with_name_and_idref_db_model)
