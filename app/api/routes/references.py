""" References routes"""
from fastapi import APIRouter, Depends

from app.api.dependencies.references import build_person_from_fields
from app.models.people import Person
from app.services.harvester.retrieval_service import RetrievalService

router = APIRouter()


@router.get(
    "",
    name="references:fetch-references-for-person-sync",
)
async def fetch_references_for_person_sync(
    person: Person = Depends(build_person_from_fields),
) -> str:
    """
    Fetch references for a person in a synchronous way
    :param person: person built from fields
    :return: json response
    """
    return str(await RetrievalService(person).retrieve())


@router.post(
    "/harvesting",
    name="references:fetch-references-for-person-async",
)
async def fetch_references_for_person_async(
    person: Person,
) -> str:
    """
    Fetch references for a person in an asynchronous way
    :param person: person built from fields
    :return: json response
    """
    return str(await RetrievalService(person).retrieve())
