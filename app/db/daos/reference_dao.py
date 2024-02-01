import datetime
from typing import List
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload

from app.db.abstract_dao import AbstractDAO
from app.db.models.entity import Entity
from app.db.models.harvesting import Harvesting
from app.db.models.identifier import Identifier
from app.db.models.reference import Reference
from app.db.models.reference_event import ReferenceEvent
from app.db.models.retrieval import Retrieval


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

    async def get_references_by_params(
        self,
        name: str,
        event_types: List[ReferenceEvent.Type],
        nullify: List[str],
        date_start: datetime.date,
        date_end: datetime.date,
    ) -> List[Reference]:
        """
        Get references by parameters
        :param name: name of the entity
        :param event_types: list of event types to fetch
        :param nullify: list of source to nullify
        :param date_start: date interval start
        :param date_end: date interval end

        :return: References
        """
        query = (
            select(Reference)
            .join(ReferenceEvent, onclause=Reference.id == ReferenceEvent.reference_id)
            .join(Harvesting, onclause=ReferenceEvent.harvesting_id == Harvesting.id)
            .join(Retrieval, onclause=Harvesting.retrieval_id == Retrieval.id)
            .join(Entity, onclause=Retrieval.entity_id == Entity.id)
            .join(Identifier, onclause=Entity.id == Identifier.entity_id)
            .options(joinedload(Reference.contributions))
            .filter(
                ReferenceEvent.type.in_(event_types),
                Identifier.type.not_in(nullify),
            )
        )

        if name:
            query = query.where(Entity.name == name)
        if date_start:
            query = query.where(Harvesting.timestamp >= date_start)
        if date_end:
            query = query.where(Harvesting.timestamp <= date_end)

        return (await self.db_session.execute(query)).unique().scalars().all()
