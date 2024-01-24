from typing import List

from pydantic import BaseModel, ConfigDict
from app.models.harvesting_error import HarvestingError

from app.models.reference_events import ReferenceEvent


class Harvesting(BaseModel):
    """
    Pydantic model matching Harvesting sql_alchemy model
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    harvester: str
    state: str

    reference_events: List[ReferenceEvent] = []
    error: HarvestingError | None
