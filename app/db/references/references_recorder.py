from typing import List

from app.db.daos.reference_dao import ReferenceDAO
from app.db.daos.reference_event_dao import ReferenceEventDAO
from app.db.models.harvesting import Harvesting as DbHarvesting
from app.db.models.reference import Reference
from app.db.models.reference_event import ReferenceEvent
from app.db.session import async_session


class ReferencesRecorder:
    """
    Class to assist harvester with the recording in database of references logic
    """

    def __init__(self, harvesting: DbHarvesting):
        self.harvesting: DbHarvesting = harvesting

    async def register_creation(
        self,
        new_ref: Reference,
    ) -> ReferenceEvent | None:
        """
        Register a new reference in the database

        :param new_ref: reference to register
        :return: the reference event
        """
        await self._create_reference(new_ref)
        async with async_session() as session:
            async with session.begin():
                return await ReferenceEventDAO(session).create_reference_event(
                    harvesting_id=self.harvesting.id,
                    reference=new_ref,
                    event_type=ReferenceEvent.Type.CREATED,
                    history=self.harvesting.history,
                )

    async def register_update(
        self,
        old_ref: Reference,
        new_ref: Reference,
    ) -> ReferenceEvent | None:
        """
        Register an update of a reference in the database

        :param old_ref: old version of the reference to update
        :param new_ref: new reference to register
        :return: the reference event
        """
        new_ref.version = old_ref.version + 1
        await self._create_reference(new_ref)
        async with async_session() as session:
            async with session.begin():
                return await ReferenceEventDAO(session).create_reference_event(
                    harvesting_id=self.harvesting.id,
                    reference=new_ref,
                    event_type=ReferenceEvent.Type.UPDATED,
                    history=self.harvesting.history,
                )

    async def register_unchanged(self, old_ref: Reference) -> ReferenceEvent | None:
        """
        Register an unchanged reference in the database

        :param old_ref: old version of the reference to update
        :return: the reference event
        """
        async with async_session() as session:
            async with session.begin():
                return await ReferenceEventDAO(session).create_reference_event(
                    harvesting_id=self.harvesting.id,
                    reference=old_ref,
                    event_type=ReferenceEvent.Type.UNCHANGED,
                    history=self.harvesting.history,
                )

    async def exists(self, new_ref: Reference) -> Reference | None:
        """
        Check if a matching reference already exists in the database

        :param new_ref: the new reference to compare with
        :return: the reference if it exists, None otherwise
        """
        async with async_session() as session:
            ref: Reference = await ReferenceDAO(
                session
            ).get_last_reference_by_source_identifier(
                new_ref.source_identifier, new_ref.harvester
            )
            return ref

    async def register_deletion(self, old_ref: Reference) -> ReferenceEvent:
        """
        Register an event for a deleted reference

        :param old_ref: the reference that was deleted
        :return: the reference event related to the deletion
        """
        async with async_session() as session:
            async with session.begin():
                return await ReferenceEventDAO(session).create_reference_event(
                    harvesting_id=self.harvesting.id,
                    reference=old_ref,
                    event_type=ReferenceEvent.Type.DELETED,
                    history=self.harvesting.history,
                )

    async def get_matching_references_before_harvesting(
        self, entity_id: int
    ) -> List[Reference]:
        """
        Get the previously harvested references for an entity

        :param entity_id: id of the entity
        :return: list of references
        """
        async with async_session() as session:
            async with session.begin():
                return await ReferenceDAO(
                    session
                ).get_previous_references_for_entity_and_harvester(
                    harvesting_id=self.harvesting.id,
                    harvester=self.harvesting.harvester,
                    entity_id=entity_id,
                )

    async def _create_reference(self, new_ref: Reference):
        async with async_session() as session:
            async with session.begin():
                session.add(new_ref)
