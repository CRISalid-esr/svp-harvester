from fastapi import APIRouter

from app.db.daos.reference_event_dao import ReferenceEventDAO
from app.db.models.reference_event import ReferenceEvent as ReferenceEventDb
from app.models.reference_events import ReferenceEvent as ReferenceEventModel
from app.db.session import async_session

router = APIRouter()


@router.get("/{reference_event_id}")
async def get_reference_event(
    reference_event_id: int, with_previous: bool = False
) -> ReferenceEventModel:
    """
    Get a reference event by id

    :param reference_event_id: id of the reference event
    :return: json representation of the reference event
    """
    async with async_session() as session:
        reference_event: ReferenceEventDb = await ReferenceEventDAO(
            session
        ).get_detailed_reference_event_by_id(reference_event_id)
        return ReferenceEventModel.model_validate(reference_event)
