"""Event types dependencies."""

from typing import List

from app.models.reference_events import ReferenceEvent


def event_types_or_default(
    events: List[ReferenceEvent.Type] = None,
) -> List[ReferenceEvent.Type]:
    """Set default event types if none are provided."""
    return events or [
        ReferenceEvent.Type.CREATED,
        ReferenceEvent.Type.UPDATED,
        ReferenceEvent.Type.DELETED,
    ]
