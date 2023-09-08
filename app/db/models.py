from typing import List

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Retrieval(Base):
    __tablename__ = "retrievals"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    harvesters: Mapped[List["Harvesting"]] = relationship(
        back_populates="retrieval", cascade="all, delete"
    )


class Harvesting(Base):
    __tablename__ = "harvestings"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    harvester = Column(String, index=True)
    retrieval_id: Mapped[int] = mapped_column(ForeignKey("retrievals.id"))
    retrieval: Mapped["Retrieval"] = relationship(back_populates="harvesters")
