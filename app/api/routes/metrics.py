""" Metrics routes"""

from fastapi import APIRouter

from app.db.daos.reference_dao import ReferenceDAO
from app.db.session import async_session

router = APIRouter()

tags_metadata = [
    {
        "name": "metrics",
        "description": "Get metrics about collected references, entities, etc.",
    }
]


@router.get("/references/by_harvester")
async def references_by_harvester() -> dict:
    """
    Get references by harvester

    :return: json representation of the references by harvester
    """
    async with async_session() as session:
        metrics = await ReferenceDAO(session).get_references_by_harvester()
    return {key: value for key, value in metrics}
