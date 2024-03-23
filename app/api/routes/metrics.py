""" Metrics routes"""

from fastapi import APIRouter

from app.db.daos.reference_dao import ReferenceDAO
from app.db.daos.reference_event_dao import ReferenceEventDAO
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


@router.get("/reference_events/by_day_and_type")
async def references_by_day_and_type() -> dict:
    """
    Get reference events by day and type

    :return: json representation of the reference events by day and type
    """
    async with async_session() as session:
        metrics = await ReferenceEventDAO(
            session
        ).get_reference_events_by_day_and_type()
    dict_tree = {}
    for date_time, event_type, value in metrics:
        # Convert datetime object to string for JSON serialization
        date_str = date_time.strftime("%d-%m-%Y")
        if date_str not in dict_tree:
            dict_tree[date_str] = {}
        if event_type not in dict_tree[date_str]:
            dict_tree[date_str][event_type] = []
        dict_tree[date_str][event_type].append(value)
    return dict_tree
