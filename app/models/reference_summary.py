import datetime
from typing import List, Tuple
from pydantic import BaseModel


class ReferenceSummary(BaseModel):
    """
    Reference summary
    """

    id: int
    timestamp: datetime.datetime
    titles: List[Tuple[str, str | None]]
    harvester: str
    source_identifier: str
    event_type: str
