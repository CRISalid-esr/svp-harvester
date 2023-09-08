""" References routes"""
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from starlette.background import BackgroundTasks

from app.api.dependencies.references import build_person_from_fields
from app.models.people import Person
from app.services.retrieval.retrieval_service import RetrievalService

router = APIRouter()


async def retrieve(retrieval_service: RetrievalService, entity: BaseModel):
    return await retrieval_service.retrieve_for(entity)


@router.get(
    "",
    name="references:fetch-references-for-person-sync",
)
async def fetch_references_sync(
    retrieval_service: Annotated[RetrievalService, Depends(RetrievalService)],
    person: Person = Depends(build_person_from_fields),
) -> str:
    """
    Fetch references for a person in a synchronous way
    :param person: person built from fields
    :return: json response
    """
    retrieval = await retrieval_service.retrieve_for(person, asynchronous=False)
    return str(retrieval.id)


@router.post(
    "/retrieval",
    name="references:fetch-references-for-person-async",
)
async def fetch_references_async(
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
