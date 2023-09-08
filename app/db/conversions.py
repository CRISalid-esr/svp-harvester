from sqlalchemy.orm import Session

from app.db.models import Retrieval, Harvesting
from app.models.entities import Entity as PydanticEntity
from app.models.identifiers import Identifier as PydanticIdentifier
from app.db.models import Entity as DbEntity
from app.db.models import Person as DbPerson
from app.db.models import Identifier as DbIdentifier


class EntityConverter:
    def __init__(self, entity: PydanticEntity):
        self.entity = entity

    def to_db_model(self) -> DbEntity:
        if self.entity.__class__.__name__ == "Person":
            return self._to_db_person()

    def _to_db_person(self) -> DbPerson:
        return DbPerson(
            last_name=self.entity.last_name,
            first_name=self.entity.first_name,
            identifiers=[
                IdentifierConverter(i).to_db_model() for i in self.entity.identifiers
            ],
        )


class IdentifierConverter:
    def __init__(self, identifier: PydanticIdentifier):
        self.identifier = identifier

    def to_db_model(self) -> DbIdentifier:
        return DbIdentifier(
            type=self.identifier.type,
            value=self.identifier.value,
        )
