from app.db.models.entity_model import Entity as DbEntity
from app.db.models.identifier_model import Identifier as DbIdentifier
from app.db.models.person_model import Person as DbPerson
from app.models.entities import Entity as PydanticEntity
from app.models.identifiers import Identifier as PydanticIdentifier


class EntityConverter:
    """
    Service to convert Pydantic entities to DB models
    """

    def __init__(self, entity: PydanticEntity):
        self.entity = entity

    def to_db_model(self) -> DbEntity:
        """Converts the entity to a DB model"""
        if self.entity.__class__.__name__ == "Person":
            return self._to_db_person()
        raise NotImplementedError(  # pragma: no cover
            "EntityConverter does not support entity type "
            f"{self.entity.__class__.__name__}"
        )

    def _to_db_person(self) -> DbPerson:
        return DbPerson(
            last_name=self.entity.last_name,
            first_name=self.entity.first_name,
            identifiers=[
                IdentifierConverter(i).to_db_model() for i in self.entity.identifiers
            ],
        )


class IdentifierConverter:
    """Service to convert Pydantic identifiers to DB models"""

    def __init__(self, identifier: PydanticIdentifier):
        self.identifier = identifier

    def to_db_model(self) -> DbIdentifier:
        """Converts the Pydantic identifier to a DB model"""
        return DbIdentifier(
            type=self.identifier.type,
            value=self.identifier.value,
        )
