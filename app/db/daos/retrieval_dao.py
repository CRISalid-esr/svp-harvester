from typing import List

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.db.abstract_dao import AbstractDAO
from app.db.models.entity import Entity
from app.db.models.harvesting import Harvesting
from app.db.models.reference_event import ReferenceEvent
from app.db.models.retrieval import Retrieval
from app.db.models.reference import Reference


class RetrievalDAO(AbstractDAO):
    """
    Data access object for Retrieval
    """

    async def create_retrieval(
        self, entity: Entity, event_types: List[ReferenceEvent.Type] = None
    ) -> Retrieval:
        """
        Create a retrieval for an entity we want to fetch references for

        :param entity: the entity we want to fetch references for
        :return: the created retrieval
        """
        retrieval = Retrieval()
        retrieval.entity = entity
        retrieval.event_types = event_types or []
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
                .joinedload(Reference.contributions)
            )
            .where(Retrieval.id == retrieval_id)
        )
        return (await self.db_session.execute(stmt)).unique().scalar_one_or_none()
