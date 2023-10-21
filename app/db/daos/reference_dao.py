from sqlalchemy import select, ScalarResult

from app.db.abstract_dao import AbstractDAO
from app.db.models.harvesting import Harvesting
from app.db.models.reference import Reference
from app.db.models.reference_event import ReferenceEvent
from app.db.models.retrieval import Retrieval


class ReferenceDAO(AbstractDAO):
    """
    Data access object for references
    """

    async def get_references_for_entity_and_harvester(
        self, entity_id: int, harvester: str
    ) -> list[Reference]:
        """
        Get the versions with the highest version number of all references
        for a given entity and harvester

        :param entity_id: id of the entity
        :param harvester: harvester name of the harvesting
        :return: list of references
        """
        query = (
            select(Reference)
            .join(ReferenceEvent)
            .join(Harvesting)
            .join(Retrieval)
            # exclude reference events where history is set to false
            .where(
                ~Reference.reference_events.any()
                | Reference.reference_events.any(ReferenceEvent.history.is_(True))
            )
            .where(Retrieval.entity_id == entity_id)
            .where(Harvesting.harvester == harvester)
        )
        references = (await self.db_session.execute(query)).unique().scalars().all()
        return ReferenceDAO._get_latest_references(references)

    @staticmethod
    def _get_latest_references(references: list[Reference]) -> list[Reference]:
        """
        Get the versions with the highest version number of all references

        :param references: list of references
        :return: list of references
        """
        latest_references = {}
        for ref in references:
            if (
                ref.source_identifier not in latest_references
                or ref.version > latest_references[ref.source_identifier].version
            ):
                latest_references[ref.source_identifier] = ref
        return list(latest_references.values())

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
