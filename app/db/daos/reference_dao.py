from sqlalchemy import select, ScalarResult

from app.db.models.harvesting import Harvesting
from app.db.models.reference_event import ReferenceEvent
from app.db.models.reference import Reference
from app.db.models.retrieval import Retrieval
from app.db.abstract_dao import AbstractDAO


class ReferenceDAO(AbstractDAO):
    """
    Data access object for references
    """

    async def get_references_for_entity_and_harvester(
            self, entity_id: int, harvester: str
    ) -> ScalarResult:
        """
        Get previously harvested references for an entity

        :param entity_id: id of the entity
        :param harvester: harvester name of the harvesting
        :return: list of references
        """
        query = (
            select(Reference)
            .join(ReferenceEvent)
            .join(Harvesting)
            .join(Retrieval)
            .where(ReferenceEvent.type != ReferenceEvent.Type.DELETED.value)
            .where(Retrieval.entity_id == entity_id)
            .where(Harvesting.harvester == harvester)
        )
        return (await self.db_session.scalars(query)).unique()

    async def get_reference_by_source_identifier(
            self, source_identifier: str, harvester: str
    ):
        """
        Get a reference by its source_identifier and the harvester it comes from

        :param source_identifier: source identifier of the reference
        :param harvester: harvester name of the harvesting it comes from
        :return: the unique reference or None if not found
        """
        query = (
            select(Reference)
            .join(ReferenceEvent)
            .join(Harvesting)
            .where(Reference.source_identifier == source_identifier)
            .where(Harvesting.harvester == harvester)
        )
        return (await self.db_session.execute(query)).unique().scalar_one_or_none()
