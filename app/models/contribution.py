from typing import List
from pydantic import BaseModel, ConfigDict

from app.models.contributor import Contributor
from app.models.organization import Organization


class Contribution(BaseModel):
    """
    Pydantic model matching Contribution sql_alchemy model
    """

    model_config = ConfigDict(from_attributes=True)

    rank: int | None

    contributor: Contributor

    role: str

    affiliations: List[Organization]
