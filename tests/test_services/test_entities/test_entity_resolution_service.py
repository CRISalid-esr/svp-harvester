"""Test the entity resolution API."""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Person, Identifier
from app.services.entities.entity_resolution_service import EntityResolutionService


@pytest.mark.asyncio
async def test_resolution_service_finds_previous_entity(async_session: AsyncSession):
    """Test that if we submit an entity with an identifier that already exists in the database,
    we get back the existing entity."""
    entity1 = Person(
        first_name="John",
        last_name="Doe",
        identifiers=[Identifier(type=Identifier.Type.IDREF.value, value="123456789")],
    )
    async_session.add(entity1)
    service = EntityResolutionService(async_session)
    entity2 = Person(
        first_name="Johnny",
        last_name="DoeVariant",
        identifiers=[Identifier(type=Identifier.Type.IDREF.value, value="123456789")],
    )
    existing_entity = await service.already_exists(entity2)
    assert existing_entity is not None
    assert existing_entity.first_name == "John"
    assert existing_entity.last_name == "Doe"
    assert len(existing_entity.identifiers) == 1
    assert existing_entity.identifiers[0].type == Identifier.Type.IDREF.value
