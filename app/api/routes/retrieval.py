import datetime
from typing import Annotated, List
from fastapi import APIRouter, Query
from pydantic import BaseModel
from app.db.daos.retrieval_dao import RetrievalDAO
from app.db.models.retrieval import Retrieval as RetrievalDB
from app.models.reference_events import ReferenceEvent
from app.models.retrieval import Retrieval as RetrievalModel

from app.db.session import async_session

router = APIRouter()


class RetrievalHistory(BaseModel):
    id: int
    entity_name: str
    identifier_type: str
    identifier_value: str
    reference_event: List[str]
    event_count: int
    document_type: List[str | None]


@router.get("/{retrieval_id}")
async def get_retrieval(retrieval_id: int) -> RetrievalModel:
    """
    Get result of a retrieval in an asynchronous way

    :param retrieval_id: id of the retrieval
    :return: json representation of the references
    """
    async with async_session() as session:
        retrieval: RetrievalDB = await RetrievalDAO(
            session
        ).get_complete_retrieval_by_id(retrieval_id)
        return RetrievalModel.model_validate(retrieval)


@router.get("")
async def get_retrievals(
    name: str = None,
    events: Annotated[List[ReferenceEvent.Type], Query()] = [],
    nullify: Annotated[List[str], Query()] = [],
    date_start: Annotated[datetime.date, Query()] = None,
    date_end: Annotated[datetime.date, Query()] = None,
) -> List[RetrievalHistory]:
    """
    Get retrieval history for a given entity
    :param name: name of the entity
    :param events: list of event types to fetch (default : "created", "updated", "deleted")
    :param nullify: list of identifiers to nullify for the person
    :param date_interval: date interval to fetch

    \f
    :param entity: entity to search
    :return: Retrieval history
    """
    async with async_session() as session:
        result = await RetrievalDAO(session).get_retrievals(
            name=name,
            event_types=events,
            nullify=nullify,
            date_start=date_start,
            date_end=date_end,
        )
        return result
