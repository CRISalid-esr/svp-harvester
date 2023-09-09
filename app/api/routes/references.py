""" References routes"""
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from starlette.responses import JSONResponse

from app.api.dependencies.references import build_person_from_fields
from app.db.daos import RetrievalDAO
from app.db.session import async_session
from app.models.people import Person
from app.services.retrieval.retrieval_service import RetrievalService

router = APIRouter()


async def retrieve(retrieval_service: RetrievalService, entity: BaseModel):
    return await retrieval_service.retrieve_for(entity)


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
    retrieval = await retrieval_service.retrieve_for(person, asynchronous=False)
    # TODO query database to get all harvesting results
    return JSONResponse({"retrieval_id": retrieval.id})


@router.post(
    "/retrieval",
    name="references:create-retrieval-for-entity-async",
)
async def create_retrieval_async(
    retrieval_service: Annotated[RetrievalService, Depends(RetrievalService)],
    person: Person,
    request: Request,
) -> str:
    """
    Fetch references for a person in an asynchronous way
    :param person: person built from fields
    :return: json response
    """
    retrieval = await retrieval_service.retrieve_for(person, asynchronous=True)
    # TODO build returned URL properly
    return f"{request.url}/{retrieval.id}"


@router.get(
    "/retrieval/{retrieval_id}",
    name="references:get-retrieval-result",
)
async def get_retrieval_result(
    retrieval_id: int,
) -> JSONResponse:
    async with async_session() as session:
        async with session.begin():
            retrieval = await RetrievalDAO(session).get_retrieval_by_id(retrieval_id)
    return retrieval
