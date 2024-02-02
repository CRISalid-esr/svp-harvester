import datetime
from typing import Annotated, List
from fastapi import APIRouter, Depends, Query
from app.api.dependencies.references import build_person_from_fields
from app.db.daos.retrieval_dao import RetrievalDAO
from app.db.models.retrieval import Retrieval as RetrievalDB
from app.models.people import Person
from app.models.reference_events import ReferenceEvent
from app.models.retrieval import Retrieval as RetrievalModel

from app.db.session import async_session
from app.models.retrieval_summary import RetrievalSummary

router = APIRouter()


@router.get("/summary")
async def get_retrievals(
    events: Annotated[List[ReferenceEvent.Type], Query()] = None,
    nullify: Annotated[List[str], Query()] = None,
    date_start: Annotated[datetime.date, Query()] = None,
    date_end: Annotated[datetime.date, Query()] = None,
    entity: Person = Depends(build_person_from_fields),
) -> List[RetrievalSummary]:
    """
    Get retrieval summary for a given entity
    :param name: name of the entity
    :param events: list of event types to fetch (default : "created", "updated", "deleted")
    :param nullify: list of identifiers to nullify for the person
    :param date_interval: date interval to fetch

    \f
    :param entity: entity to search
    :return: Retrieval history
    """
    events = events if events else []
    nullify = nullify if nullify else []

    async with async_session() as session:
        result = await RetrievalDAO(session).get_retrievals(
            event_types=events,
            nullify=nullify,
            date_interval=(date_start, date_end),
            entity=entity,
        )
        return result


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
