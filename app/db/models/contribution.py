from enum import Enum
from typing import List

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.affiliations import affiliations_table
from app.db.session import Base


class Contribution(Base):
    """
    Model for persistence of contributions
    """

    class Role(Enum):
        """
        Rôles of contributors
        see https://documentation.abes.fr/aidescienceplusabes/index.html#roles
        """

        AUTHOR = "Author"
        CONTRIBUTOR = "Contributor"
        COMPOSER = "Composer"
        EDITOR = "Editor"
        ILLUSTRATOR = "Illustrator"
        TRANSLATOR = "Translator"

    __tablename__ = "contributions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    rank: Mapped[int] = mapped_column(nullable=True)

    contributor_id: Mapped[int] = mapped_column(ForeignKey("contributors.id"))
    contributor: Mapped["app.db.models.contributor.Contributor"] = relationship(
        "app.db.models.contributor.Contributor",
        back_populates="contributions",
        lazy="joined",
        cascade="all",
    )

    reference_id: Mapped[int] = mapped_column(ForeignKey("references.id"))
    reference: Mapped["app.db.models.reference.Reference"] = relationship(
        "app.db.models.reference.Reference",
        back_populates="contributions",
        lazy="raise",
    )

    role: Mapped[str] = mapped_column(
        nullable=False, index=True, default=Role.AUTHOR.value
    )

    affiliations: Mapped[
        List["app.db.models.organization.Organization"]
    ] = relationship(
        "app.db.models.organization.Organization",
        secondary=affiliations_table,
        lazy="joined",
        back_populates="contributions",
    )
