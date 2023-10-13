from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column


class VersionedRecord:
    """Adds versioning capabilities to a record."""

    hash: Mapped[str] = mapped_column(String)
    version: Mapped[int] = mapped_column(index=True, default=0)
