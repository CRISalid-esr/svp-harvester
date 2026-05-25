from typing import List

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Topic(Base):
    __tablename__ = "topics"

    id: Mapped[int] = mapped_column(primary_key=True)
    source_id: Mapped[str] = mapped_column(nullable=False, unique=True, index=True)
    uri: Mapped[str] = mapped_column(nullable=False, unique=True)
    display_name: Mapped[str] = mapped_column(nullable=False)

    reference_topics: Mapped[
        List["app.db.models.reference_topic.ReferenceTopic"]
    ] = relationship(
        "app.db.models.reference_topic.ReferenceTopic",
        back_populates="topic",
        cascade="all, delete-orphan",
    )
