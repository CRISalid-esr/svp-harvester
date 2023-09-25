""" References routes"""
from typing import Annotated

from fastapi import APIRouter, Depends
from starlette.responses import JSONResponse

from app.api.dependencies.references import build_person_from_fields
from app.config import get_app_settings
from app.db.daos import RetrievalDAO
from app.db.session import async_session
from app.models.people import Person
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
    person: Person = Depends(build_person_from_fields),
) -> JSONResponse:
    """
    Fetch references for a person in a synchronous way
    :param person: person built from fields
    :return: json response
    """
    retrieval = await retrieval_service.register(person)
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
    person: Person,
) -> JSONResponse:
    """
    Fetch references for a person in an in_background way
    :param settings: app settings
    :param retrieval_service: retrieval service
    :param person: person built from fields
    :return: json response
    """
    retrieval = await retrieval_service.register(person)
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
        retrieval = await RetrievalDAO(session).get_complete_retrieval_by_id(
            retrieval_id
        )
    return RetrievalModel.model_validate(retrieval)
