from app.db.abstract_dao import AbstractDAO
from app.db.models.reference import Reference
from app.db.models.reference_event import ReferenceEvent


class ReferenceEventDAO(AbstractDAO):
    """
    Data access object for reference events
    """

    async def create_reference_event(
        self,
        reference: Reference,
        harvesting_id: int,
        event_type: ReferenceEvent.Type,
    ) -> ReferenceEvent:
        """
        Create a reference event for a reference

        :param reference: reference to which the event is related
        :param harvesting_id: harvesting id to which the event belongs
        :param event_type: state of the event
        :return: the created reference event
        """
        reference_event = ReferenceEvent(type=event_type.value)
        reference_event.reference = reference
        reference_event.harvesting_id = harvesting_id
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