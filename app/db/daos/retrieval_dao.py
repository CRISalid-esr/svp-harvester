import datetime
from typing import List

from sqlalchemy import func, or_, select
from sqlalchemy.orm import joinedload

from app.db.abstract_dao import AbstractDAO
from app.db.models.references_document_type import references_document_type_table
from app.db.models.document_type import DocumentType
from app.db.models.entity import Entity
from app.db.models.harvesting import Harvesting
from app.db.models.identifier import Identifier
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

    async def get_retrievals(
        self,
        name: str,
        event_types: List[ReferenceEvent.Type],
        nullify: List[str],
        date_start: datetime.date,
        date_end: datetime.date,
    ) -> List[Retrieval]:
        """
        Get retrieval history for a given entity
        :param name: name of the entity
        :param event_types: list of event types to fetch
        :param nullify: list of source to nullify
        :param date_start: date interval start
        :param date_end: date interval end

        :return: Retrieval history
        """
        event_types.append("None")

        stmt = (
            select(
                Retrieval.id,
                (Entity.name).label("entity_name"),
                (
                    func.array_agg(func.distinct(Identifier.type, Identifier.value))
                ).label("identifier_type"),
                (func.array_agg(ReferenceEvent.type.distinct())).label(
                    "reference_event"
                ),
                (func.count(ReferenceEvent.id.distinct())).label("event_count"),
                (func.array_agg(DocumentType.label.distinct())).label("document_type"),
                (
                    func.array_agg(
                        func.distinct(
                            Harvesting.harvester,
                            Harvesting.state,
                        )
                    )
                ).label("harvesting_state"),
            )
            .join(Harvesting, onclause=Retrieval.id == Harvesting.retrieval_id)
            .join(Entity, onclause=Retrieval.entity_id == Entity.id)
            .join(Identifier, onclause=Entity.id == Identifier.entity_id)
            .outerjoin(
                ReferenceEvent, onclause=Harvesting.id == ReferenceEvent.harvesting_id
            )
            .outerjoin(Reference, onclause=ReferenceEvent.reference_id == Reference.id)
            .outerjoin(
                references_document_type_table,
                onclause=Reference.id == references_document_type_table.c.reference_id,
            )
            .outerjoin(
                DocumentType,
                onclause=DocumentType.id
                == references_document_type_table.c.document_type_id,
            )
            .filter(
                # Add None in case of no event so we can still see the harvesting failed
                or_(ReferenceEvent.type.in_(event_types), ReferenceEvent.type == None),
                Identifier.type.not_in(nullify),
            )
            .group_by(Retrieval.id, Entity.name)
        )

        # TODO SEE Date ?
        # TODO Filter ID_ENTITY for each type
        if name:
            stmt = stmt.where(Entity.name == name)
        if date_start:
            stmt = stmt.where(Harvesting.timestamp >= date_start)
        if date_end:
            stmt = stmt.where(Harvesting.timestamp <= date_end)

        return await self.db_session.execute(stmt)
