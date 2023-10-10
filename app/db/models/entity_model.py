from typing import List

from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.db.session import Base


class Entity(Base):
    """
    Base Model for entities for which we want to fetch references
    """

    __tablename__ = "entities"

    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str]
    name: Mapped[str] = mapped_column(nullable=True)

    __mapper_args__ = {
        "polymorphic_identity": "entity",
        "polymorphic_on": "type",
    }

    identifiers: Mapped[List["app.db.models.identifier_model.Identifier"]] = relationship(
        "app.db.models.identifier_model.Identifier",
        back_populates="entity", cascade="all, delete-orphan", lazy="joined"
    )

    retrievals: Mapped[List["app.db.models.retrieval_model.Retrieval"]] = relationship(
        "app.db.models.retrieval_model.Retrieval",
        back_populates="entity", cascade="all, delete", lazy="raise"
    )

    @validates("identifiers", include_removes=False, include_backrefs=True)
    def _validate_no_more_than_one_identifier_of_same_type(self, _, new_identifier):
        """
        Validate that no more than one identifier of the same type is present

        :param key:
        :param address:
        :return:
        """
        if new_identifier.type is None:
            raise ValueError("Identifier type cannot be None")
        if new_identifier.value is None:
            raise ValueError("Identifier value cannot be None")
        if self.has_identifier_of_type(new_identifier.type):
            raise ValueError(
                f"Identifier of type {new_identifier.type} already present for {self}"
            )
        return new_identifier

    def get_identifier(self, identifier_type: str) -> str | None:
        """
        Get identifier value for a given type

        :param identifier_type: type of the identifier
        :return: the identifier or None if not found
        """
        for identifier in self.identifiers:
            if identifier.type == identifier_type:
                return identifier.value
        return None

    def has_identifier_of_type_and_value(
            self, identifier_type: str, identifier_value: str
    ) -> bool:
        """
        Check if an identifier of a given type and value is present

        :param identifier_type: type of the identifier
        :param identifier_value: value of the identifier
        :return: True if the identifier is present, False otherwise
        """
        for identifier in self.identifiers:
            if (
                    identifier.type == identifier_type
                    and identifier.value == identifier_value
            ):
                return True
        return False

    def has_identifier_of_type(self, identifier_type: str) -> bool:
        """
        Check if an identifier of a given type is present

        :param identifier_type: type of the identifier
        :return: True if the identifier is present, False otherwise
        """
        for identifier in self.identifiers:
            if identifier and identifier.type == identifier_type:
                return True
        return False
