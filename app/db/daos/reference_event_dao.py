from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.db.abstract_dao import AbstractDAO
from app.db.models.harvesting import Harvesting
from app.db.models.reference import Reference
from app.db.models.reference_event import ReferenceEvent
from app.db.models.retrieval import Retrieval


# pylint: disable=duplicate-code
class ReferenceEventDAO(AbstractDAO):
    """
    Data access object for reference events
    """

    async def create_reference_event(
        self,
        reference: Reference,
        harvesting_id: int,
        event_type: ReferenceEvent.Type,
        history: bool = True,
    ) -> ReferenceEvent:
        """
        Create a reference event for a reference

        :param reference: reference to which the event is related
        :param harvesting_id: harvesting id to which the event belongs
        :param event_type: state of the event
        :param history: if True, the event will be recorded
               in the history of the harvestings for this entity
        :return: the created reference event
        """
        reference_event = ReferenceEvent(
            type=event_type.value, history=history, harvesting_id=harvesting_id
        )
        reference_event.reference = reference
        self.db_session.add(reference_event)
        return reference_event

    async def get_reference_event_by_id(
        self, reference_event_id: int
    ) -> ReferenceEvent | None:
        """
        Get a reference event by its id

        :param reference_event_id:
        :return:
        """
        return await self.db_session.get(ReferenceEvent, reference_event_id)

    async def get_detailed_reference_event_by_id(
        self, reference_event_id: int
    ) -> ReferenceEvent | None:
        """
        Get a reference event by its id with reference, harvesting and entity
        :param reference_event_id:  id of the reference event
        :return:   the reference event or None if not found
        """
        stmt = (
            select(ReferenceEvent)
            .options(
                joinedload(ReferenceEvent.harvesting)
                .joinedload(Harvesting.retrieval)
                .joinedload(Retrieval.entity)
            )
            .where(ReferenceEvent.id == reference_event_id)
        )
        return (await self.db_session.execute(stmt)).unique().scalar_one_or_none()
