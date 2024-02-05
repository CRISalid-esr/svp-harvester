import datetime
from typing import Annotated, List
from fastapi import Query

from app.models.reference_events import ReferenceEvent


async def common_parameters(
    events: Annotated[List[ReferenceEvent.Type], Query()] = None,
    nullify: Annotated[List[str], Query()] = None,
    harvester: Annotated[List[str], Query()] = None,
    date_start: datetime.date = None,
    date_end: datetime.date = None,
) -> dict:
    """
    Common parameters for references and retrieval get requests
    """

    return {
        "events": events if events else [],
        "nullify": nullify if nullify else [],
        "harvester": harvester if harvester else [],
        "date_start": date_start,
        "date_end": date_end,
    }
