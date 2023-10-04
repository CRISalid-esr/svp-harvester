from typing import List

from pydantic import BaseModel, ConfigDict

from app.models.entities import Entity
from app.models.harvesting import Harvesting


class Retrieval(BaseModel):
    """
    Pydantic model matching Retrieval sql_alchemy model
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    harvestings: List[Harvesting] = []

    entity: Entity | None = None
