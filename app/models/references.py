from typing import List

from pydantic import BaseModel, ConfigDict

from app.models.concepts import Concept
from app.models.literal_fields import LiteralFields


class Reference(BaseModel):
    """
    Pydantic model matching Reference sql_alchemy model
    """

    model_config = ConfigDict(from_attributes=True)

    source_identifier: str

    id: int

    titles: List[LiteralFields] = []
    subtitles: List[LiteralFields] = []
    subjects: List[Concept] = []
