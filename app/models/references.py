from typing import List

from pydantic import BaseModel, ConfigDict

from app.models.concepts import Concept
from app.models.subtitles import Subtitle
from app.models.titles import Title


class Reference(BaseModel):
    """
    Pydantic model matching Reference sql_alchemy model
    """

    model_config = ConfigDict(from_attributes=True)

    source_identifier: str
    harvester: str

    id: int

    titles: List[Title] = []
    subtitles: List[Subtitle] = []
    subjects: List[Concept] = []
