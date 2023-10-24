"""References dependencies."""
from typing import Annotated, List

from fastapi import Depends, Query

from app.api.dependencies.event_types import event_types_or_default
from app.config import get_app_settings
from app.models.reference_events import ReferenceEvent
from app.services.retrieval.retrieval_service import RetrievalService
from app.settings.app_settings import AppSettings


def build_retrieval_service_from_fields(
    settings: Annotated[AppSettings, Depends(get_app_settings)],
    history_safe_mode: Annotated[bool, Query()] = False,
    identifiers_safe_mode: Annotated[bool, Query()] = False,
    nullify: Annotated[List[str], Query()] = None,
    events: Annotated[List[ReferenceEvent.Type], Query()] = None,
) -> RetrievalService:
    """
    Build a retrieval service from the provided fields.
    :param settings:   app settings
    :param history_safe_mode:  history safe mode
    :param identifiers_safe_mode: identifiers safe mode
    :param nullify:   list of identifiers to nullify for the person
    :param events:   list of event types to fetch (default : "created", "updated", "deleted")
    :return:
    """
    return RetrievalService(
        settings=settings,
        history_safe_mode=history_safe_mode,
        identifiers_safe_mode=identifiers_safe_mode,
        nullify=nullify,
        events=event_types_or_default(events),
    )
