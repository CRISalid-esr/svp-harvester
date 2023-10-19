""" References routes"""
from typing import Annotated, List

from fastapi import APIRouter, Depends
from starlette.responses import JSONResponse

from app.api.dependencies.event_types import event_types_or_default
from app.api.dependencies.references import build_person_from_fields
from app.config import get_app_settings
from app.db.daos.retrieval_dao import RetrievalDAO
from app.db.models.retrieval import Retrieval as DbRetrieval
from app.db.session import async_session
from app.models.people import Person
from app.models.reference_events import ReferenceEvent
from app.models.retrieval import Retrieval as RetrievalModel
from app.services.retrieval.retrieval_service import RetrievalService
from app.settings.app_settings import AppSettings

router = APIRouter()


@router.get(
    "",
    name="references:create-retrieval-for-entity-sync",
)
async def create_retrieval_sync(
    retrieval_service: Annotated[RetrievalService, Depends(RetrievalService)],
    entity: Person = Depends(build_person_from_fields),
    nullify: List[str] = None,
    events: Annotated[
        List[ReferenceEvent.Type], Depends(event_types_or_default)
    ] = None,
) -> JSONResponse:
    """
    Fetch references for a person in a synchronous way
    :param entity: person built from fields
    :param nullify: list of identifiers to nullify for the person
    :param events: list of event types to fetch (default : "created", "updated", "deleted")
    :return: json response
    """
    # TODO none of the entity identifiers should be listed in nullify
    retrieval = await retrieval_service.register(entity, events, nullify=nullify)
    await retrieval_service.run(in_background=False)
    # TODO query database to get all harvesting results
    return JSONResponse({"retrieval_id": retrieval.id})


@router.post(
    "/retrieval",
    name="references:create-retrieval-for-entity-async",
)
async def create_retrieval_async(
    settings: Annotated[AppSettings, Depends(get_app_settings)],
    retrieval_service: Annotated[RetrievalService, Depends(RetrievalService)],
    person: Person | None,
    nullify: List[str] = None,
    events: Annotated[
        List[ReferenceEvent.Type], Depends(event_types_or_default)
    ] = None,
) -> JSONResponse:
    """
    Fetch references for a person in an in_background way

    :param settings: app settings
    :param retrieval_service: retrieval service
    :param person: entity built from fields
    :param nullify: list of identifiers to nullify for the person
    :param events: list of event types to fetch (default : "created", "updated", "deleted")
    :return: json response
    """
    # TODO none of the entitty identifiers should be listed in nullify
    retrieval = await retrieval_service.register(
        entity=person, events=events, nullify=nullify
    )
    await retrieval_service.run(in_background=True)
    # TODO build returned URL properly
    return JSONResponse(
        {
            "retrieval_id": retrieval.id,
            "retrieval_url": f"{settings.api_host}"
            f"{settings.api_prefix}/{settings.api_version}"
            f"/references/retrieval/{retrieval.id}",
        }
    )


@router.get(
    "/retrieval/{retrieval_id}",
    name="references:get-retrieval-result",
    response_model=RetrievalModel,
)
async def get_retrieval_result(
    retrieval_id: int,
) -> RetrievalModel:
    """
    Get result of a retrieval in an asynchronous way

    :param retrieval_id: id of the retrieval
    :return: json representation of the references
    """
    async with async_session() as session:
        retrieval: DbRetrieval = await RetrievalDAO(
            session
        ).get_complete_retrieval_by_id(retrieval_id)
    return RetrievalModel.model_validate(retrieval)
