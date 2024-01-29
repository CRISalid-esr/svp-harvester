from typing import List

from pydantic import BaseModel, ConfigDict, Field

from app.models.abstracts import Abstract
from app.models.concepts import Concept
from app.models.contribution import Contribution
from app.models.document_type import DocumentType
from app.models.subtitles import Subtitle
from app.models.titles import Title


class Reference(BaseModel):
    """
    Pydantic model matching Reference sql_alchemy model
    """

    model_config = ConfigDict(from_attributes=True)

    source_identifier: str
    harvester: str

    id: int = Field(exclude=True)

    titles: List[Title] = []
    subtitles: List[Subtitle] = []
    abstracts: List[Abstract] = []
    subjects: List[Concept] = []
    document_type: List[DocumentType] = []
    contributions: List[Contribution] = []
