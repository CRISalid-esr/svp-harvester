from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base


class DocumentType(Base):
    """
    Model for persistance of document types
    """

    __tablename__ = "document_type"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    code: Mapped[str] = mapped_column(nullable=False, index=False, unique=True)

    label: Mapped[str] = mapped_column(nullable=True, index=False)
