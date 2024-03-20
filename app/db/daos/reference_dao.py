import datetime
from typing import List
from sqlalchemy import and_, or_, select, func
from sqlalchemy.orm import joinedload, raiseload

from app.db.abstract_dao import AbstractDAO
from app.db.daos.entity_dao import EntityDAO
from app.db.models.entity import Entity
from app.db.models.harvesting import Harvesting
from app.db.models.identifier import Identifier
from app.db.models.reference import Reference
from app.db.models.reference_event import ReferenceEvent
from app.db.models.retrieval import Retrieval
from app.db.models.title import Title
from app.db.models.person import Person
from app.models.reference_summary import ReferenceSummary
from app.utilities.string_utilities import split_string


# pylint: disable=not-callable
class ReferenceDAO(AbstractDAO):
    """
    Data access object for references
    """

    async def get_previous_references_for_entity_and_harvester(
        self,
        entity_id: int,
        harvester: str,
        harvesting_id: int,
    ) -> list[Reference]:
        """
        Get the references discovered by the harvesting that occurred before the given harvesting
        for the given entity and harvester

        :param harvesting_id: id of the current harvesting
        :param entity_id: id of the entity
        :param harvester: harvester name of the harvesting
        :return: list of references
        """
        # Fin the last completed harvesting id with history set to true
        # for the given entity and harvester
        subquery = (
            # pylint: disable=not-callable
            select(func.max(Harvesting.id).label("max_harvesting_id"))
            .join(Retrieval)
            .where(Harvesting.history.is_(True))
            .where(Retrieval.entity_id == entity_id)
            .where(Harvesting.harvester == harvester)
            .where(Harvesting.id != harvesting_id)
            .where(Harvesting.state == Harvesting.State.COMPLETED.value)
        ).subquery()
        # find all references related to the last harvesting
        # that are not of "deleted" type
        query = (
            select(Reference)
            .options(raiseload("*"))
            .join(ReferenceEvent)
            .join(
                subquery, ReferenceEvent.harvesting_id == subquery.c.max_harvesting_id
            )
            .where(ReferenceEvent.type != ReferenceEvent.Type.DELETED.value)
        )
        # return the references
        return (await self.db_session.execute(query)).unique().scalars().all() or []

    async def get_references_by_source_identifier(
        self, source_identifier: str, harvester: str
    ):
        """
        Get all references by their source_identifier and the harvester they come from

        :param source_identifier: source identifier of the references
        :param harvester: harvester name of the harvesting they come from
        :return: the references
        """
        query = (
            select(Reference)
            .where(Reference.source_identifier == source_identifier)
            .where(Reference.harvester == harvester)
            .order_by(Reference.version.asc())
        )
        return (await self.db_session.execute(query)).scalars().unique().all()

    async def get_last_reference_by_source_identifier(
        self, source_identifier: str, harvester: str
    ):
        """
        Get the reference with the highest version number
        with a given source_identifier and harvester

        :param source_identifier: source identifier of the reference
        :param harvester: harvester name of the harvesting it comes from
        :return: the unique reference or None if not found
        """
        query = (
            select(Reference)
            .options(raiseload("*"))
            .where(Reference.source_identifier == source_identifier)
            .where(Reference.harvester == harvester)
            # where there is no reference event
            # or exists at least one reference event with history set to true
            .where(
                ~Reference.reference_events.any()
                | Reference.reference_events.any(ReferenceEvent.history.is_(True))
            )
            .order_by(Reference.version.desc())
        )
        return (await self.db_session.execute(query)).scalars().first()

    async def get_references_summary(
        self,
        text_search: str,
        filter_harvester: dict[List, List],
        date_interval: tuple[datetime.date, datetime.date],
        entity: Person,
    ) -> List[ReferenceSummary]:
        """
        Get references sumaru by parameters
        :param text_search: text to search
        :param filter_harvester: filter for the harvester (event_types, nullify, harvester)
        :param date_interval: date interval to fetch
        :param entity: entity to search

        :return: References
        """
        date_start, date_end = date_interval
        if entity:
            entity_id = EntityDAO(self.db_session).entity_filter_subquery(entity)
        else:
            entity_id = EntityDAO(self.db_session).get_all_entities_subquery()

        query = (
            select(
                Reference.id.label("id"),
                Harvesting.timestamp.label("timestamp"),
                (
                    func.array_agg(func.distinct(Title.value, Title.language)).label(
                        "titles"
                    )
                ),
                Reference.harvester.label("harvester"),
                Reference.source_identifier.label("source_identifier"),
                ReferenceEvent.type.label("event_type"),
            )
            .join(ReferenceEvent, onclause=Reference.id == ReferenceEvent.reference_id)
            .join(Harvesting, onclause=ReferenceEvent.harvesting_id == Harvesting.id)
            .join(Retrieval, onclause=Harvesting.retrieval_id == Retrieval.id)
            .join(entity_id, onclause=Retrieval.entity_id == entity_id.c.id)
            .join(Entity, onclause=entity_id.c.id == Entity.id)
            .join(Identifier, onclause=entity_id.c.id == Identifier.entity_id)
            .join(Title)
            .filter(
                ReferenceEvent.type.in_(filter_harvester["event_types"]),
                Identifier.type.not_in(filter_harvester["nullify"]),
                func.lower(Reference.harvester).in_(
                    [func.lower(h) for h in filter_harvester["harvester"]]
                ),
            )
            .order_by(Harvesting.timestamp.desc())
            .group_by(Harvesting.timestamp, Reference.id, ReferenceEvent.type)
        )

        if entity and entity.name:
            names = split_string(entity.name)
            query = query.filter(
                and_(*[entity_id.c.name.like(f"%{name}%") for name in names])
            )
        if date_start:
            query = query.where(Harvesting.timestamp >= date_start)
        if date_end:
            query = query.where(Harvesting.timestamp <= date_end)

        query = self._filter_text_search(query, text_search)
        return await self.db_session.execute(query)

    async def get_complete_reference_by_id(self, reference_id: int) -> Reference | None:
        """
        Get a reference by its id

        :param reference_id: id of the reference
        :return: the reference or None if not found
        """
        stmt = (
            select(Reference)
            .options(joinedload(Reference.contributions))
            .where(Reference.id == reference_id)
        )

        return (await self.db_session.execute(stmt)).unique().scalar_one_or_none()

    def _filter_text_search(self, query, text_search: str):
        """
        Filter the query by text search

        :param query: query to filter
        :param text_search: text to search
        :return: the filtered query
        """
        if text_search == "":
            return query
        return query.filter(
            or_(
                Entity.name.like(f"%{text_search}%"),
                Identifier.value.like(f"%{text_search}%"),
                Title.value.like(f"%{text_search}%"),
            )
        )
