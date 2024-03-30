"""References dependencies."""
from typing import Annotated, List

from fastapi import Query

from app.api.dependencies.event_types import event_types_or_default
from app.models.reference_events import ReferenceEvent
from app.services.retrieval.retrieval_service import RetrievalService


def build_retrieval_service_from_fields(
    identifiers_safe_mode: Annotated[bool, Query()] = False,
    harvesters: Annotated[List[str], Query()] = None,
    nullify: Annotated[List[str], Query()] = None,
    events: Annotated[List[ReferenceEvent.Type], Query()] = None,
) -> RetrievalService:
    """
    Build a retrieval service from the provided fields.
    :param identifiers_safe_mode: identifiers safe mode
    :param harvesters:   list of harvesters to fetch (default : None, all harvesters)
    :param nullify:   list of identifiers to nullify for the person
    :param events:   list of event types to fetch (default : "created", "updated", "deleted")
    :return:
    """

    return RetrievalService(
        identifiers_safe_mode=identifiers_safe_mode,
        nullify=nullify,
        events=event_types_or_default(events),
        harvesters=harvesters,
    )
