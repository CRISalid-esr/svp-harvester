"""Test the entity resolution API."""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_app_settings
from app.db.models.person import Person
from app.db.models.identifier import Identifier
from app.services.entities.entity_resolution_service import EntityResolutionService


@pytest.mark.asyncio
async def test_resolution_service_finds_previous_entity(async_session: AsyncSession):
    """Test that if we submit an entity with an identifier that already exists in the database,
    we get back the existing entity."""
    entity1 = Person(
        name="John Doe",
        identifiers=[Identifier(type="idref", value="123456789")],
    )
    async_session.add(entity1)
    service = EntityResolutionService(async_session)
    entity2 = Person(
        name="Johnny DoeVariant",
        identifiers=[Identifier(type="idref", value="123456789")],
    )
    existing_entity = await service.resolve(entity2)
    assert existing_entity is not None
    assert existing_entity.name == "John Doe"
    assert len(existing_entity.identifiers) == 1
    assert existing_entity.identifiers[0].type == "idref"


@pytest.mark.asyncio
async def test_resolution_service_updates_previous_entity(async_session: AsyncSession):
    """
    GIVEN an entity with an identifier that already exists in the database
    WHEN we submit an entity with the same identifier and another identifier
    THEN the existing entity is updated with the new identifier

    :param async_session: async session fixture
    :return: None
    """
    entity1 = Person(
        name="John Doe",
        identifiers=[Identifier(type="idref", value="123456789")],
    )
    async_session.add(entity1)
    service = EntityResolutionService(async_session)
    entity2 = Person(
        name="Johnny DoeVariant",
        identifiers=[
            Identifier(type="idref", value="123456789"),
            Identifier(type="id_hal_i", value="987654321"),
        ],
    )
    existing_entity = await service.resolve(entity2)
    assert existing_entity is not None
    assert existing_entity.name == "John Doe"
    assert len(existing_entity.identifiers) == 2
    assert existing_entity.identifiers[0].type == "idref"
    assert existing_entity.identifiers[1].type == "id_hal_i"
    assert existing_entity.identifiers[1].value == "987654321"


@pytest.mark.asyncio
async def test_resolution_service_respects_identifier_hierarchy(
    async_session: AsyncSession,
):
    """
    GIVEN an identifiers configuration file where idref has a lower priority than id_hal_i
    and an entity that exists in database with an idref and an id_hal_i
    WHEN we submit an entity with the same idref and another id_hal_i
    THEN the existing entity is updated with the new id_hal_i

    :param async_session: async session fixture
    :return: None
    """
    settings = get_app_settings()
    assert settings.identifiers[0].get("key") == "idref"
    assert settings.identifiers[2].get("key") == "id_hal_i"
    assert settings.identifiers[0].get("priority") < settings.identifiers[2].get(
        "priority"
    )
    entity1 = Person(
        name="John Doe",
        identifiers=[
            Identifier(type="idref", value="123456789"),
            Identifier(type="id_hal_i", value="987654321"),
        ],
    )
    async_session.add(entity1)
    service = EntityResolutionService(async_session)
    entity2 = Person(
        name="Johnny DoeVariant",
        identifiers=[
            Identifier(type="idref", value="123456789"),
            Identifier(type="id_hal_i", value="999999999"),
        ],
    )
    existing_entity = await service.resolve(entity2)
    assert existing_entity is not None
    assert len(existing_entity.identifiers) == 2
    assert existing_entity.identifiers[0].type == "idref"
    assert existing_entity.identifiers[1].type == "id_hal_i"
    assert existing_entity.identifiers[1].value == "999999999"


@pytest.mark.asyncio
async def test_resolution_service_reassigns_identifier_to_another_entity(
    async_session: AsyncSession,
):
    """
    GIVEN an identifiers configuration file where idref has a lower priority than orcid
    and an entity that exists in database with idref 1
    and another entity that exists in database with idref 2 and orcid 1
    WHEN we submit an entity with idref 1 and orcid 1
    THEN the existing entity with idref 2 and orcid 1 loses its orcid
    and the existing entity with idref 1 gains orcid 1


    :param async_session: async session fixture
    :return: None
    """
    settings = get_app_settings()
    assert settings.identifiers[0].get("key") == "idref"
    assert settings.identifiers[1].get("key") == "orcid"
    assert settings.identifiers[0].get("priority") < settings.identifiers[1].get(
        "priority"
    )
    entity1 = Person(
        name="John Doe",
        identifiers=[
            Identifier(type="idref", value="123456789"),
            Identifier(type="orcid", value="000000000"),
        ],
    )
    async_session.add(entity1)
    entity2 = Person(
        name="Jane Doe",
        identifiers=[
            Identifier(type="idref", value="987654321"),
            Identifier(type="orcid", value="111111111"),
        ],
    )
    async_session.add(entity2)
    service = EntityResolutionService(async_session)
    entity3 = Person(
        name="Johnny DoeVariant",
        identifiers=[
            Identifier(type="idref", value="123456789"),
            Identifier(type="orcid", value="111111111"),
        ],
    )
    existing_entity = await service.resolve(entity3)
    assert existing_entity is not None
    assert len(existing_entity.identifiers) == 2
    assert existing_entity.has_identifier_of_type("idref")
    assert existing_entity.has_identifier_of_type_and_value("orcid", "111111111")
    assert len(entity2.identifiers) == 1
    assert entity2.has_identifier_of_type_and_value("idref", "987654321")


@pytest.mark.asyncio
async def test_resolution_service_deletes_entity_if_it_loses_is_only_identifier(
    async_session: AsyncSession,
):
    """
    GIVEN an identifiers configuration file where idref has a lower priority than orcid
    and an entity that exists in database with idref 1
    and another entity that exists in database with orcid 1
    WHEN we submit an entity with idref 1 and orcid 1
    THEN the existing entity with idref 1 gains orcid 1
    and the existing entity with orcid 1 is deleted
    """
    settings = get_app_settings()
    assert settings.identifiers[0].get("key") == "idref"
    assert settings.identifiers[1].get("key") == "orcid"
    assert settings.identifiers[0].get("priority") < settings.identifiers[1].get(
        "priority"
    )
    entity1 = Person(
        name="John Doe",
        identifiers=[
            Identifier(type="idref", value="123456789"),
        ],
    )
    async_session.add(entity1)
    entity2 = Person(
        name="Jane Doe",
        identifiers=[
            Identifier(type="orcid", value="111111111"),
        ],
    )
    async_session.add(entity2)
    entity2_id = entity2.id
    service = EntityResolutionService(async_session)
    entity3 = Person(
        name="Johnny DoeVariant",
        identifiers=[
            Identifier(type="idref", value="123456789"),
            Identifier(type="orcid", value="111111111"),
        ],
    )
    existing_entity = await service.resolve(entity3)
    assert existing_entity is not None
    assert len(existing_entity.identifiers) == 2
    assert existing_entity.has_identifier_of_type("idref")
    assert existing_entity.has_identifier_of_type_and_value("orcid", "111111111")
    assert len(entity2.identifiers) == 0
    assert await async_session.get(Person, entity2_id) is None


@pytest.mark.asyncio
async def test_complex_situation_with_existing_ids_and_conflicts(
    async_session: AsyncSession,
):
    """
    GIVEN an identifiers configuration file where idref has a lower priority than orcid
    and orcid has a lower priority than id_hal_i
    and id_hal_i has a lower priority than researcher_id
    and an entity that exists in database with idref 1 and id_hal_i 1
    and another entity that exists in database with idref 2 and orcid 2 and id_hal_i 2
    and another entity that exists in database with orcid 3 and id_hal_i 3
    and another entity that exists in database with researcher_id 4
    WHEN we submit an entity with idref 1 and orcid 2 and id_hal_i 3 and researcher_id 4
    THEN the existing entity with idref 2 and orcid 2 and id_hal_i 2 loses its orcid
    and the existing entity with orcid 3 and id_hal_i 3 loses its id_hal_i
    and the existing entity with researcher_id 4 is deleted
    and the existing entity with idref 1 and id_hal_i 1 gains orcid 2 and researcher_id 4
    and its id_hal_i is replaced by id_hal_i 3

    :param async_session: async session fixture
    :return: None
    """
    settings = get_app_settings()
    assert settings.identifiers[0].get("key") == "idref"
    assert settings.identifiers[1].get("key") == "orcid"
    assert settings.identifiers[2].get("key") == "id_hal_i"
    assert settings.identifiers[4].get("key") == "researcher_id"
    assert settings.identifiers[0].get("priority") < settings.identifiers[1].get(
        "priority"
    )
    assert settings.identifiers[1].get("priority") < settings.identifiers[2].get(
        "priority"
    )
    assert settings.identifiers[2].get("priority") < settings.identifiers[4].get(
        "priority"
    )
    entity1 = Person(
        name="John Doe",
        identifiers=[
            Identifier(type="id_hal_i", value="1"),
            Identifier(type="idref", value="1"),
        ],
    )
    async_session.add(entity1)
    entity2 = Person(
        name="Jane Doe",
        identifiers=[
            Identifier(type="id_hal_i", value="2"),
            Identifier(type="idref", value="2"),
            Identifier(type="orcid", value="2"),
        ],
    )
    async_session.add(entity2)
    entity3 = Person(
        name="Johnny Doe",
        identifiers=[
            Identifier(type="id_hal_i", value="3"),
            Identifier(type="orcid", value="3"),
        ],
    )
    async_session.add(entity3)
    entity4 = Person(
        name="Jenny Doe",
        identifiers=[
            Identifier(type="researcher_id", value="4"),
        ],
    )
    async_session.add(entity4)
    entity4_id = entity4.id
    service = EntityResolutionService(async_session)
    entity5 = Person(
        name="Johnny DoeVariant",
        identifiers=[
            Identifier(type="id_hal_i", value="3"),
            Identifier(type="idref", value="1"),
            Identifier(type="researcher_id", value="4"),
            Identifier(type="orcid", value="2"),
        ],
    )
    existing_entity = await service.resolve(entity5)
    assert existing_entity is not None
    assert len(existing_entity.identifiers) == 4
    assert existing_entity.has_identifier_of_type_and_value("idref", "1")
    assert existing_entity.has_identifier_of_type_and_value("orcid", "2")
    assert existing_entity.has_identifier_of_type_and_value("id_hal_i", "3")
    assert existing_entity.has_identifier_of_type_and_value("researcher_id", "4")
    assert len(entity2.identifiers) == 2
    assert entity2.has_identifier_of_type_and_value("idref", "2")
    assert entity2.has_identifier_of_type_and_value("id_hal_i", "2")
    assert len(entity3.identifiers) == 1
    assert entity3.has_identifier_of_type_and_value("orcid", "3")
    assert await async_session.get(Person, entity4_id) is None


@pytest.mark.asyncio
async def test_resolution_service_removes_nullified_identifiers(
    async_session: AsyncSession,
):
    """
    GIVEN an existing person entity with idhal and idref
    WHEN we submit a new person entity with the same idref and 'idhal' to nullify
    THEN the existing entity loses its idhal

    :param async_session: async session fixture
    :return: None
    """
    entity1 = Person(
        first_name="John",
        last_name="Doe",
        identifiers=[
            Identifier(type="id_hal_i", value="1"),
            Identifier(type="idref", value="1"),
        ],
    )
    async_session.add(entity1)
    service = EntityResolutionService(async_session)
    entity2 = Person(
        first_name="John",
        last_name="Doe",
        identifiers=[
            Identifier(type="idref", value="1"),
        ],
    )
    existing_entity = await service.resolve(entity2, nullify=["id_hal_i"])
    assert existing_entity is not None
    assert len(existing_entity.identifiers) == 1
    assert existing_entity.has_identifier_of_type_and_value("idref", "1")
