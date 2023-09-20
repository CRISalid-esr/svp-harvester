from app.db.daos import IdentifierDAO
from app.db.models import Entity
from app.db.session import async_session


class EntityResolutionService:
    """
    Service to find entities that have been submitted yet
    and resolve potential identifier conflicts
    """

    async def already_exists(self, entity: Entity) -> Entity:
        """Check if entity with at least one identifier in common already exists in database"""
        # TODO handle the case where multiple entities are found
        async with async_session() as session:
            for identifier in entity.identifiers:
                existing = await IdentifierDAO(
                    session
                ).get_identifier_and_entity_by_type_and_value(
                    identifier_type=identifier.type, identifier_value=identifier.value
                )
                if existing:
                    return existing[1]
