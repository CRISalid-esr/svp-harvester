"""Tests for the Person model."""
import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.identifier import (
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


@pytest.mark.asyncio
async def test_identifier_type_value_pair_cannot_be_added_twice(
    async_session: AsyncSession,
    person_with_name_and_idref_db_model,
    person_with_name_and_id_hal_i_db_model,
):
    """
    GIVEN an entity (Person) with an Identifier of a specific type-value pair
    WHEN another Identifier with the same type-value pair is associated with another entity
    THEN check a IntegrityError is raised
         due to violation of the unique constraint on type and value
    """

    # Add the person along with its id and commit the transaction
    async_session.add(person_with_name_and_idref_db_model)
    async_session.add(person_with_name_and_id_hal_i_db_model)
    await async_session.commit()

    # Create a second Identifier with the same type and value
    duplicate_identifier = DbIdentifier(
        type="idref",
        value=person_with_name_and_idref_db_model.get_identifier("idref"),
        entity_id=person_with_name_and_id_hal_i_db_model.id,
    )
    with pytest.raises(IntegrityError):
        async_session.add(duplicate_identifier)
        await async_session.commit()
