from typing import List
from datetime import datetime

import semver
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import validates

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
    harvester_version: str
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

    @validates("harvester_version")
    def validate_version(self, key, version):
        try:
            parsed_version = semver.VersionInfo.parse(version)
            return str(parsed_version)
        except ValueError:
            raise ValueError(f"Invalid semantic version: {version} for field {key}")
