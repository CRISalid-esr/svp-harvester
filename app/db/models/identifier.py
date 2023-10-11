from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.config import get_app_settings
from app.db.session import Base


class Identifier(Base):
    """
    Model for persistence of identifiers
    """

    __tablename__ = "identifiers"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    type: Mapped[str] = mapped_column(nullable=False, index=True)
    value: Mapped[str] = mapped_column(nullable=False, index=True)
    entity_id: Mapped[int] = mapped_column(ForeignKey("entities.id"))
    entity: Mapped["app.db.models.entity.Entity"] = relationship(
        "app.db.models.entity.Entity", back_populates="identifiers", lazy="raise")

    @validates("type", include_removes=False, include_backrefs=True)
    def _valide_identifier_is_referenced_by_settings(self, _, new_type):
        """
        Validate that the identifier is referenced by the settings
        """
        settings = get_app_settings()
        if new_type not in [
            identifier.get("key") for identifier in settings.identifiers
        ]:
            raise ValueError("Identifier type is not referenced by settings")
        return new_type
