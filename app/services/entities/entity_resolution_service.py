from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_app_settings
from app.db.daos.identifier_dao import IdentifierDAO
from app.db.daos.entity_dao import EntityDAO
from app.db.models.entity import Entity as DbEntity


class EntityResolutionService:
    """
    Service to find entities that have been submitted yet
    and resolve potential identifier conflicts
    """

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def resolve(self, entity_to_resolve: DbEntity) -> DbEntity | None:
        """
        Find an entity that has yet been submitted by its identifiers
        and resolve potential identifier conflicts
        :param entity_to_resolve: entity to resolve (non registered to database)
        :return: resolved entity (registered to database if it exists)
        """
        # create a list of existing entities with at least one identifier
        # that matches one of the identifiers of the entity we want to resolve
        identifier_dao = IdentifierDAO(self.db_session)
        entity_dao = EntityDAO(self.db_session)
        submitted_identifiers = entity_to_resolve.identifiers
        matching_entities = await identifier_dao.get_entities_by_identifiers(
            submitted_identifiers
        )
        # order the list of existing entities
        # by the priority of the identifier that matches
        # one of the identifiers of the entity we want to resolve
        settings = get_app_settings()
        matching_entities = sorted(
            list(matching_entities),
            key=lambda e: min(
                settings.identifiers[i].get("key")
                for i in range(len(settings.identifiers))
                if settings.identifiers[i].get("key") == e.identifiers[0].type
            ),
        )
        # if the list is empty, the entity does not exist yet
        if not matching_entities:
            return None
        # if the list is not empty, the entity exists
        # the elected entity is the first one in the list
        # (the one with the highest priority identifier)
        elected_entity: DbEntity = matching_entities[0]
        # we need to update the elected entity with the identifiers of the entity we want to resolve
        # and to remove the identifiers from the elected entities if they already exist
        entities_to_delete = []
        # dont use db entities in loop as some of them will be deleted and the loop will break
        identifiers_type_and_values = [(i.type, i.value) for i in submitted_identifiers]
        for identifier_type, identifier_value in identifiers_type_and_values:
            # check if the elected entity has the identifier to add
            # if it does not, add it
            if not elected_entity.has_identifier_of_type_and_value(
                identifier_type, identifier_value
            ):
                # add the identifier to the elected entity
                # or override the existing value if it already exists
                entity_dao.add_or_override_identifier(
                    elected_entity, identifier_type, identifier_value
                )
                # search for an existing entity that has the identifier to add
                # in the list of existing entities
                # if it exists, remove the identifier from it
                for existing_entity in matching_entities:
                    if existing_entity == elected_entity:
                        continue
                    if existing_entity.has_identifier_of_type_and_value(
                        identifier_type, identifier_value
                    ):
                        entity_dao.remove_identifier_by_type_and_value(
                            existing_entity, identifier_type, identifier_value
                        )
                        # if the existing entity has no more identifiers, delete it
                        if not existing_entity.identifiers:
                            entities_to_delete.append(existing_entity)
        # delete the entities that have no more identifiers
        for entity_to_delete in entities_to_delete:
            await entity_dao.delete(entity_to_delete)
        # return the elected entity
        return elected_entity
