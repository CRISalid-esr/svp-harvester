""" References routes"""
from typing import Annotated

from fastapi import APIRouter, Depends
from starlette import status
from starlette.datastructures import URL
from starlette.requests import Request
from starlette.responses import JSONResponse, RedirectResponse

from app.api.dependencies.references import build_person_from_fields
from app.api.dependencies.retrieval_service import build_retrieval_service_from_fields
from app.config import get_app_settings
from app.db.daos.retrieval_dao import RetrievalDAO
from app.db.models.retrieval import Retrieval as DbRetrieval
from app.db.session import async_session
from app.models.people import Person
from app.models.retrieval import Retrieval as RetrievalModel
from app.services.retrieval.retrieval_service import RetrievalService
from app.settings.app_settings import AppSettings

router = APIRouter()

tags_metadata = [
    {
        "name": "retrieval",
        "description": "Operations with users. The **login** logic is also here.",
    },
    {
        "name": "items",
        "description": "Manage items. So _fancy_ they have their own docs.",
        "externalDocs": {
            "description": "Items external docs",
            "url": "https://fastapi.tiangolo.com/",
        },
    },
]


@router.get(
    "",
    tags=["retrieval"],
    response_class=RedirectResponse,
    status_code=status.HTTP_302_FOUND,
)
async def create_retrieval_sync(
    request: Request,
    retrieval_service: Annotated[
        RetrievalService, Depends(build_retrieval_service_from_fields)
    ],
    entity: Person = Depends(build_person_from_fields),
) -> RedirectResponse:
    """
    Fetch references for a person in a synchronous way

    - **history_safe_mode**: if True, this retrieval won't update entity harvesting history
    - **identifiers_safe_mode**: if True, this retrieval won't update entity identifiers
    - **nullify**: list of identifiers to nullify for the person
                    (in case they've been previously associated)
    - **harvesters**: list of harvesters to use
                        (default : None, all eligible harvesters will be used)
    - **events**: list of event types to fetch (default : "created", "updated", "deleted")
    - **name**: name of the entity to fetch references for (optional, for lisibility only)
    - **idref**: idref of the entity
    - **orcid**: orcid of the entity
    - **id_hal_i**: id_hal_i of the entity
    - **id_hal_s**: id_hal_s of the entity

    \f
    :param retrieval_service: retrieval service
    :param entity: entity built from fields
    :return: Retrieval representation with harvestings and results
    """
    # TODO none of the entity identifiers should be listed in nullify
    retrieval = await retrieval_service.register(entity)
    await retrieval_service.run(in_background=False)
    redirect_url = URL(
        request.url_for("get_retrieval_result", retrieval_id=retrieval.id)
    )
    # no other way to pass the url to the redirect response
    return RedirectResponse(redirect_url._url)  # pylint: disable=protected-access


@router.post(
    "/retrieval",
    name="references:create-retrieval-for-entity-async",
)
async def create_retrieval_async(
    settings: Annotated[AppSettings, Depends(get_app_settings)],
    retrieval_service: Annotated[RetrievalService, Depends(RetrievalService)],
    person: Person | None,
) -> JSONResponse:
    """
    Fetch references for a person in an in_background way

    \f
    :param settings: app settings
    :param retrieval_service: retrieval service
    :param person: entity built from fields
    :return: json response
    """
    # TODO none of the entitty identifiers should be listed in nullify
    retrieval = await retrieval_service.register(
        entity=person,
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
