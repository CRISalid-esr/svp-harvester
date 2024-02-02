import datetime
from typing import List, Tuple
from pydantic import BaseModel


class RetrievalSummary(BaseModel):
    id: int
    timestamp: datetime.datetime
    entity_name: str
    identifier_type: List[Tuple[str, str]]
    harvesting_state: List[Tuple[str, str, str | None, int]]
    event_count: int
    document_type: List[str | None]
