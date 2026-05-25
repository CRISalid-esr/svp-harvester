from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class ReferenceTopic(Base):
    __tablename__ = "reference_topics"

    reference_id: Mapped[int] = mapped_column(
        ForeignKey("references.id"), primary_key=True, index=True
    )
    topic_id: Mapped[int] = mapped_column(
        ForeignKey("topics.id"), primary_key=True, index=True
    )
    score: Mapped[float] = mapped_column(nullable=False)

    topic: Mapped["app.db.models.topic.Topic"] = relationship(
        "app.db.models.topic.Topic",
        back_populates="reference_topics",
        lazy="joined",
    )
    reference: Mapped["app.db.models.reference.Reference"] = relationship(
        "app.db.models.reference.Reference",
        back_populates="topics",
        lazy="raise",
    )
