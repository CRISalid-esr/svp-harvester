from app.db.abstract_dao import AbstractDAO
from app.db.models.entity import Entity
from app.db.models.identifier import Identifier


class EntityDAO(AbstractDAO):
    """
    Data access object for abstract entities
    """

    async def get_entity_by_id(self, entity_id: int) -> Entity | None:
        """
        Get an entity by its id

        :param entity_id: id of the entity
        :return: the entity or None if not found
        """
        return await self.db_session.get(Entity, entity_id)

    @staticmethod
    def add_or_override_identifier(
            entity: Entity, identifier_type: str, identifier_value: str
    ):
        """
        Add an identifier of the given type to an entity,
        or override it if it already exists

        :param entity: the entity to add the identifier to
        :param identifier_type: type of the identifier
        :param identifier_value: value of the identifier
        :return: None
        """
        for existing_identifier in entity.identifiers:
            if existing_identifier.type == identifier_type:
                existing_identifier.value = identifier_value
                return
        entity.identifiers.append(
            Identifier(type=identifier_type, value=identifier_value)
        )

    @staticmethod
    def remove_identifier_by_type_and_value(
            entity: Entity, identifier_type: str, identifier_value: str
    ):
        """
        Remove an identifier from an entity

        :param entity: the entity to remove the identifier from
        :param identifier_type: type of the identifier to remove
        :param identifier_value: value of the identifier to remove
        :return: None
        """
        for identifier in entity.identifiers:
            if (
                    identifier.type == identifier_type
                    and identifier.value == identifier_value
            ):
                entity.identifiers.remove(identifier)
                return
        assert (
            False
        ), f"Identifier of type {identifier_type} with value {identifier_value} not found"

    async def delete(self, entity: Entity) -> None:
        """
        Delete an entity from the database

        :param entity: the entity to delete
        :return: None
        """
        await self.db_session.delete(entity)
