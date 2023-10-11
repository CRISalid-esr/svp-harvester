from typing import List

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.references_subject import references_subjects_table
from app.db.session import Base


class Reference(Base):
    """
    Model for persistence of references
    """

    __tablename__ = "references"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    source_identifier: Mapped[str] = mapped_column(nullable=False, index=True)
    titles: Mapped[List["app.db.models.title.Title"]] = relationship(
        "app.db.models.title.Title",
        back_populates="reference", cascade="all, delete", lazy="joined"
    )
    subtitles: Mapped[List["app.db.models.subtitle.Subtitle"]] = relationship(
        "app.db.models.subtitle.Subtitle",
        back_populates="reference", cascade="all, delete", lazy="joined"
    )

    subjects: Mapped[List["app.db.models.concept.Concept"]] = relationship(
        "app.db.models.concept.Concept",
        secondary=references_subjects_table)

    reference_events: Mapped[
        List["app.db.models.reference_event.ReferenceEvent"]
    ] = relationship(
        "app.db.models.reference_event.ReferenceEvent",
        back_populates="reference", cascade="all, delete", lazy="raise"
    )

    hash: Mapped[str] = mapped_column(String, index=True)
