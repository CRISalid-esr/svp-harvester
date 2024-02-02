from typing import Annotated, List
from fastapi import APIRouter, Depends
from app.api.dependencies.common_parameters import common_parameters
from app.api.dependencies.references import build_person_from_fields
from app.db.daos.retrieval_dao import RetrievalDAO
from app.db.models.retrieval import Retrieval as RetrievalDB
from app.models.people import Person
from app.models.retrieval import Retrieval as RetrievalModel

from app.db.session import async_session
from app.models.retrieval_summary import RetrievalSummary

router = APIRouter()


@router.get("/summary")
async def get_retrievals(
    params: Annotated[dict, Depends(common_parameters)],
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
    async with async_session() as session:
        result = await RetrievalDAO(session).get_retrievals_summary(
            event_types=params["events"],
            nullify=params["nullify"],
            date_interval=(params["date_start"], params["date_end"]),
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
