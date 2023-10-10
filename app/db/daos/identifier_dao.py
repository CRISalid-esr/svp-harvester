from sqlalchemy import select, Row

from app.db.abstract_dao import AbstractDAO
from app.db.models.entity_model import Entity
from app.db.models.identifier_model import Identifier


class IdentifierDAO(AbstractDAO):
    """
    Data access object for identifiers
    """

    async def get_identifier_and_entity_by_type_and_value(
            self, identifier_type: str, identifier_value: str
    ) -> Row[Identifier, Entity] | None:
        """
        Get an identifier (along with the associated entity) by its type and value

        :param identifier_type: type of the identifier
        :param identifier_value: value of the identifier
        :return: the identifier or None if not found
        """
        query = (
            select(Identifier, Entity)
            .join(Entity)
            .where(
                Identifier.type == identifier_type, Identifier.value == identifier_value
            )
        )

        return (await self.db_session.execute(query)).unique().first()

    async def get_entities_by_identifiers(self, identifiers):
        """
        Get a list of entities matching the given identifiers

        :param identifiers: list of identifiers
        :return: list of entities
        """
        query = (
            select(Entity)
            .join(Identifier)
            .where(Identifier.type.in_(identifier.type for identifier in identifiers))
            .where(Identifier.value.in_(identifier.value for identifier in identifiers))
        )
        return (await self.db_session.scalars(query)).unique()
