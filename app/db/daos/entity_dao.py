from sqlalchemy import and_, select

from app.db.abstract_dao import AbstractDAO
from app.db.models.entity import Entity
from app.db.models.identifier import Identifier
from app.db.models.person import Person


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

    async def take_or_create_identifier(
        self, entity: Entity, identifier_type: str, identifier_value: str
    ):
        """
        Add an identifier of the given type to an entity,
        or override it if it already exists

        :param entity: the entity to add the identifier to
        :param identifier_type: type of the identifier
        :param identifier_value: value of the identifier
        :return: None
        """
        # search if the identifier of given type and value exists in the whole table
        query = select(Identifier).where(
            Identifier.type == identifier_type, Identifier.value == identifier_value
        )
        identifier_of_same_type_and_value = (
            (await self.db_session.execute(query)).unique().scalar_one_or_none()
        )
        if (
            identifier_of_same_type_and_value
            and identifier_of_same_type_and_value.entity_id == entity.id
        ):
            # if the identifier of same type and value belongs to the entity
            # do nothing
            return
        # search if entity already has identifier of same type
        identifier_of_same_type = next(
            (
                identifier
                for identifier in entity.identifiers
                if identifier.type == identifier_type
            ),
            None,
        )
        if identifier_of_same_type_and_value:
            # if the entity already has an identifier of same type
            # delete it
            if identifier_of_same_type:
                entity.identifiers.remove(identifier_of_same_type)
            # attach the identifier of same type and value to the entity
            entity.identifiers.append(identifier_of_same_type_and_value)
            return
        if identifier_of_same_type:
            # if the entity already has an identifier of same type
            # update its value
            identifier_of_same_type.value = identifier_value
            return
        # in last extremity, create a new identifier
        entity.identifiers.append(
            Identifier(type=identifier_type, value=identifier_value)
        )

    def remove_identifier_by_type_and_value(
        self, entity: Entity, identifier_type: str, identifier_value: str
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

    def entity_filter_subquery(self, entity: Person):
        """
        Get a subquery to filter entities by their identifiers
        """
        entity_filter = and_(True)
        if entity.identifiers:
            entity_filter = and_(
                Identifier.type.in_([i.type for i in entity.identifiers]),
                Identifier.value.in_([i.value for i in entity.identifiers]),
            )

        return (
            select(Entity.id.label("id"), Entity.name.label("name"))
            .join(Identifier, onclause=Entity.id == Identifier.entity_id)
            .group_by(Entity.id)
            .filter(entity_filter)
        ).subquery("entity_id")
