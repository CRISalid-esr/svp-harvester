import datetime
from typing import List, Tuple

from sqlalchemy import func, or_, select, and_
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
from app.models.people import Person


# pylint: disable=not-callable
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
        event_types: List[ReferenceEvent.Type],
        nullify: List[str],
        date_interval: Tuple[datetime.date, datetime.date],
        entity: Person,
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
        date_start, date_end = date_interval

        harvesting_event_count = self._harvesting_event_count_subquery(
            event_types, nullify
        )

        entity_id = self._entity_filter_subquery(entity)

        stmt = (
            select(
                Retrieval.id,
                Retrieval.timestamp,
                (entity_id.c.name).label("entity_name"),
                (
                    func.array_agg(func.distinct(Identifier.type, Identifier.value))
                ).label("identifier_type"),
                (func.count(ReferenceEvent.id.distinct())).label("event_count"),
                (func.array_agg(DocumentType.label.distinct())).label("document_type"),
                (
                    func.array_agg(
                        func.distinct(
                            Harvesting.harvester,
                            Harvesting.state,
                            harvesting_event_count.c.type_event,
                            harvesting_event_count.c.count,
                        )
                    )
                ).label("harvesting_state"),
            )
            .join(Harvesting, onclause=Retrieval.id == Harvesting.retrieval_id)
            .join(
                harvesting_event_count,
                onclause=Harvesting.id == harvesting_event_count.c.id,
            )
            .join(entity_id, onclause=Retrieval.entity_id == entity_id.c.id)
            .join(Identifier, onclause=entity_id.c.id == Identifier.entity_id)
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
            .group_by(Retrieval.id, entity_id.c.name)
        )

        if entity.name:
            stmt = stmt.where(Entity.name == entity.name)
        if date_start:
            stmt = stmt.where(Harvesting.timestamp >= date_start)
        if date_end:
            stmt = stmt.where(Harvesting.timestamp <= date_end)

        return await self.db_session.execute(stmt)

    def _harvesting_event_count_subquery(self, event_types, nullify):
        event_types.append(None)
        return (
            select(
                Harvesting.id,
                ReferenceEvent.type.label("type_event"),
                func.count(ReferenceEvent.id.distinct().label("count")),
            )
            .outerjoin(
                ReferenceEvent, onclause=ReferenceEvent.harvesting_id == Harvesting.id
            )
            .filter(
                # Add None in case of no event so we can still see the harvesting failed
                or_(ReferenceEvent.type.in_(event_types), ReferenceEvent.type == None),
                Identifier.type.not_in(nullify),
            )
            .group_by(Harvesting.id, ReferenceEvent.type)
        ).subquery("event_count_harvesting")

    def _entity_filter_subquery(self, entity: Person):
        entity_filter = and_(1 == 1)
        if entity.identifiers:
            entity_filter = and_(
                Identifier.type.in_([i.type for i in entity.identifiers]),
                Identifier.value.in_([i.value for i in entity.identifiers]),
            )

        return (
            select(Entity.id.label("id"), Entity.name.label("name"))
            .join(Identifier, onclause=Entity.id == Identifier.entity_id)
            .group_by(Entity.id)
            .filter(entity_filter)
        ).subquery("entity_id")
