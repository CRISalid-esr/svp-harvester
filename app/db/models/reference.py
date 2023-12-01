from typing import List

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.abstract import Abstract
from app.db.models.references_subject import references_subjects_table
from app.db.models.versioned_record import VersionedRecord
from app.db.session import Base

# temporary imports
from app.db.models.contribution import Contribution  # pylint: disable=unused-import
from app.db.models.contributor import Contributor  # pylint: disable=unused-import
from app.db.models.organization import Organization  # pylint: disable=unused-import
from app.db.models.title import Title  # pylint: disable=unused-import
from app.db.models.subtitle import Subtitle  # pylint: disable=unused-import


class Reference(Base, VersionedRecord):
    """
    Model for persistence of references
    """

    __tablename__ = "references"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    source_identifier: Mapped[str] = mapped_column(nullable=False, index=True)

    # The reference should stay traceable to the harvester that created it
    # even if the harvesting history is cleaned up
    harvester: Mapped[str] = mapped_column(nullable=False, index=True)

    titles: Mapped[List["app.db.models.title.Title"]] = relationship(
        "app.db.models.title.Title",
        back_populates="reference",
        cascade="all, delete-orphan",
        lazy="joined",
    )
    subtitles: Mapped[List["app.db.models.subtitle.Subtitle"]] = relationship(
        "app.db.models.subtitle.Subtitle",
        back_populates="reference",
        cascade="all, delete-orphan",
        lazy="joined",
    )
    abstracts: Mapped[List[Abstract]] = relationship(
        "app.db.models.abstract.Abstract",
        back_populates="reference",
        cascade="all, delete-orphan",
        lazy="joined",
    )

    subjects: Mapped[List["app.db.models.concept.Concept"]] = relationship(
        "app.db.models.concept.Concept",
        secondary=references_subjects_table,
        lazy="joined",
    )

    reference_events: Mapped[
        List["app.db.models.reference_event.ReferenceEvent"]
    ] = relationship(
        "app.db.models.reference_event.ReferenceEvent",
        back_populates="reference",
        cascade="all, delete",
        lazy="raise",
    )

    contributions: Mapped[
        List["app.db.models.contribution.Contribution"]
    ] = relationship(
        "app.db.models.contribution.Contribution",
        back_populates="reference",
        cascade="all, delete",
        lazy="raise",
    )
