from typing import List

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import ARRAY

from app.db.session import Base


class Book(Base):
    """
    Model for persistence of books
    """

    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    source: Mapped[str] = mapped_column(nullable=False, index=True)

    title: Mapped[str] = mapped_column(nullable=True, index=True)
    title_variants: Mapped[List[str]] = mapped_column(
        ARRAY(String), nullable=True, default=[]
    )
    isbn10: Mapped[str] = mapped_column(nullable=True, index=True, unique=True)
    isbn13: Mapped[str] = mapped_column(nullable=True, index=True, unique=True)
    publisher: Mapped[str] = mapped_column(nullable=True, index=False)

    references: Mapped[List["app.db.models.reference.Reference"]] = relationship(
        "app.db.models.reference.Reference",
        back_populates="book",
        lazy="raise",
    )
