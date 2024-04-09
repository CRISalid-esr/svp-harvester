from typing import List
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.book import Book
from app.models.issue import Issue
from app.models.abstracts import Abstract
from app.models.concepts import Concept
from app.models.contribution import Contribution
from app.models.document_type import DocumentType
from app.models.reference_identifier import ReferenceIdentifier
from app.models.subtitles import Subtitle
from app.models.titles import Title


class Reference(BaseModel):
    """
    Pydantic model matching Reference sql_alchemy model
    """

    model_config = ConfigDict(from_attributes=True)

    source_identifier: str
    harvester: str
    identifiers: List[ReferenceIdentifier] = []
    titles: List[Title] = []
    subtitles: List[Subtitle] = []
    abstracts: List[Abstract] = []
    subjects: List[Concept] = []
    document_type: List[DocumentType] = []
    contributions: List[Contribution] = []
    issue: Issue | None = None
    page: str | None = None
    book: Book | None = None
    issued: datetime | None = None
    created: datetime | None = None
    version: int
