from typing import Type

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

    async def resolve(
        self,
        entity_to_resolve: Type[DbEntity],
        nullify: list[str] = None,
        identifiers_safe_mode: bool = False,
    ):
        """
        Find an entity that has yet been submitted by its identifiers
        and resolve potential identifier conflicts
        :param entity_to_resolve: entity to resolve (non registered to database)
        :param nullify: list of identifiers to set to null
        :param identifiers_safe_mode: if True, do not update identifiers nor
               update identifiers of existing entities
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
        # if the safe mode is enabled, don't update the identifiers
        if identifiers_safe_mode:
            return elected_entity
        self._remove_nullified_identifiers(elected_entity, nullify)
        # override the name of the elected entity with the name of the entity to resolve
        elected_entity.name = entity_to_resolve.name

        # dont use db entities in loop as some of them will be deleted and the loop will break
        identifiers_type_and_values = [(i.type, i.value) for i in submitted_identifiers]
        for identifier_type, identifier_value in identifiers_type_and_values:
            await entity_dao.take_or_create_identifier(
                elected_entity, identifier_type, identifier_value
            )
        return elected_entity

    @staticmethod
    def _remove_nullified_identifiers(existing_entity, nullify):
        if not nullify:
            return
        identifiers = existing_entity.identifiers
        for identifier in identifiers:
            if identifier.type in nullify:
                existing_entity.identifiers.remove(identifier)
