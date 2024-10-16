""" References routes"""

from typing import Annotated, List

from fastapi import APIRouter, Depends, Query
from starlette import status
from starlette.datastructures import URL
from starlette.requests import Request
from starlette.responses import JSONResponse, RedirectResponse

from app.api.dependencies.references import (
    build_person_from_fields,
    build_person_from_fields_optional,
)
from app.api.dependencies.retrieval_service import build_retrieval_service_from_fields
from app.config import get_app_settings
from app.db.daos.reference_dao import ReferenceDAO
from app.db.daos.retrieval_dao import RetrievalDAO
from app.db.models.retrieval import Retrieval as DbRetrieval
from app.db.session import async_session
from app.models.people import Person
from app.models.reference_summary import ReferenceSummary
from app.models.references import Reference
from app.models.retrieval import Retrieval as RetrievalModel
from app.services.retrieval.retrieval_service import RetrievalService
from app.services.summary.fetch_summary import fetch_summary
from app.settings.app_settings import AppSettings
from app.api.dependencies.common_parameters import common_parameters

router = APIRouter()

tags_metadata = [
    {
        "name": "retrieval",
        "description": "Operations with users. The **login** logic is also here.",
    }
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

    - **identifiers_safe_mode**: if True, this retrieval won't update entity identifiers
    - **nullify**: list of identifiers to nullify for the person
                    (in case they've been previously associated)
    - **harvesters**: list of harvesters to use
                        (default : None, all eligible harvesters will be used)
    - **events**: list of event types to fetch (default : "created", "updated", "deleted")
    - **fetch_enhancements**: if True, this retrieval will fetch enhanced references
                    even if the event type is not among the requested ones
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
    retrieval = await retrieval_service.register(
        entity=person,
    )
    await retrieval_service.run(in_background=True)
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
        ).get_retrieval_display_info_by_id(retrieval_id)
    return RetrievalModel.model_validate(retrieval)


@router.get("/summary")
async def get_references(
    params: Annotated[dict, Depends(common_parameters)],
    text_search: Annotated[str, Query()] = "",
    entity: Person = Depends(build_person_from_fields_optional),
) -> List[ReferenceSummary]:
    """
    Get references by parameters
    :param name: name of the entity
    :param events: list of event types to fetch
    :param nullify: list of source to nullify
    :param harvester: harvester to fetch
    :param date_start: date interval start
    :param date_end: date interval end

    :return: References
    """

    async with async_session() as session:
        return await fetch_summary(
            ReferenceDAO, session, params, entity, {"text_search": text_search}
        )


@router.get("/by_id_and_version")
async def get_reference_by_source_identifier_version(
    harvester: str,
    source_identifier: str,
    version: int,
) -> Reference:
    """
    Get a reference by its harvester, source_identifier and version

    :param harvester: harvester that created the reference
    :param source_identifier: identifier of the reference in the source
    :param version: version of the reference
    :return: the reference
    """
    async with async_session() as session:
        reference = await ReferenceDAO(
            session
        ).get_complete_reference_by_harvester_source_identifier_version(
            harvester, source_identifier, version
        )
        return Reference.model_validate(reference)


@router.get("/{reference_id}")
async def get_reference_by_id(reference_id: int) -> Reference:
    """
    Get a reference by its id

    :param reference_id: id of the reference
    :return: the reference
    """
    async with async_session() as session:
        reference = await ReferenceDAO(session).get_complete_reference_by_id(
            reference_id
        )
        return Reference.model_validate(reference)
