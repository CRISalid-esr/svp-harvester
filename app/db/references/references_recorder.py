from app.db.daos.reference_dao import ReferenceDAO
from app.db.daos.reference_event_dao import ReferenceEventDAO
from app.db.models.harvesting_model import Harvesting
from app.db.models.reference_event_model import ReferenceEvent
from app.db.models.reference_model import Reference
from app.db.session import async_session


class ReferencesRecorder:
    """
    Class to assist harvester with the recording in database of references logic
    """

    async def register(
            self, harvesting: Harvesting, new_ref: Reference
    ) -> ReferenceEvent:
        """
        Register a new reference in the database
        :param new_ref: The reference to register
        :return: None
        """
        event_type = None
        ref = None
        if old_ref := await self.exists(new_ref, harvesting):
            if old_ref.hash != new_ref.hash:
                event_type = ReferenceEvent.Type.UPDATED
                await self._update_reference(old_ref, new_ref)
            else:
                event_type = ReferenceEvent.Type.UNCHANGED
            ref = old_ref
        else:
            event_type = ReferenceEvent.Type.CREATED
            await self._create_reference(new_ref)
            ref = new_ref
        async with async_session() as session:
            async with session.begin():
                return await ReferenceEventDAO(session).create_reference_event(
                    harvesting=harvesting,
                    reference=ref,
                    event_type=event_type,
                )

    async def exists(
            self, new_ref: Reference, harvesting: Harvesting
    ) -> Reference | None:
        """
        Check if a reference already exists in the database
        :param new_ref: the new reference to compare with
        :param harvesting: the current harvesting
        :return: the reference if it exists, None otherwise
        """
        async with async_session() as session:
            return await ReferenceDAO(session).get_reference_by_source_identifier(
                new_ref.source_identifier, harvesting.harvester
            )

    async def register_deletion(
            self, harvesting: Harvesting, old_ref: Reference
    ) -> ReferenceEvent:
        """
        Register an event for a deleted reference

        :param harvesting: the harvesting during which the deletion was detected
        :param old_ref: the reference that was deleted
        :return: the reference event related to the deletion
        """
        async with async_session() as session:
            async with session.begin():
                return await ReferenceEventDAO(session).create_reference_event(
                    harvesting=harvesting,
                    reference=old_ref,
                    event_type=ReferenceEvent.Type.DELETED,
                )

    async def get_previous_references(
            self, entity_id: int, harvester: str
    ) -> list[Reference]:
        """
        Get the previously harvested references for an entity

        :param entity_id: id of the entity
        :return: list of references
        """
        async with async_session() as session:
            async with session.begin():
                return await ReferenceDAO(
                    session
                ).get_references_for_entity_and_harvester(entity_id, harvester)

    async def _create_reference(self, new_ref: Reference):
        async with async_session() as session:
            async with session.begin():
                session.add(new_ref)

    def _update_reference(self, old_ref, new_ref):
        pass
