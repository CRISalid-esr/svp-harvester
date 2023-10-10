from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.db.abstract_dao import AbstractDAO
from app.db.models.entity_model import Entity
from app.db.models.harvesting_model import Harvesting
from app.db.models.reference_event_model import ReferenceEvent
from app.db.models.retrieval_model import Retrieval


class RetrievalDAO(AbstractDAO):
    """
    Data access object for Retrieval
    """

    async def create_retrieval(self, entity: Entity) -> Retrieval:
        """
        Create a retrieval for an entity we want to fetch references for

        :param entity: the entity we want to fetch references for
        :return: the created retrieval
        """
        retrieval = Retrieval()
        retrieval.entity = entity
        self.db_session.add(retrieval)
        return retrieval

    async def get_retrieval_by_id(self, retrieval_id: int) -> Retrieval | None:
        """
        Get a retrieval by its id

        :param retrieval_id: id of the retrieval
        :return: the retrieval or None if not found
        """
        return await self.db_session.get(Retrieval, retrieval_id)

    async def get_complete_retrieval_by_id(self, retrieval_id: int) -> Retrieval | None:
        """
        Get a retrieval by its id with all its references

        :param retrieval_id: id of the retrieval
        :return: the retrieval or None if not found
        """
        stmt = (
            select(Retrieval)
            .options(
                joinedload(Retrieval.harvestings)
                .joinedload(Harvesting.reference_events)
                .joinedload(ReferenceEvent.reference)
            )
            .where(Retrieval.id == retrieval_id)
        )
        return (await self.db_session.execute(stmt)).unique().scalar_one_or_none()
