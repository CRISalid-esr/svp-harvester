from typing import List

from sqlalchemy import ScalarResult

from app.api.dependencies.event_types import event_types_or_default
from app.db.daos.reference_dao import ReferenceDAO
from app.db.daos.reference_event_dao import ReferenceEventDAO
from app.db.models.reference import Reference
from app.db.models.reference_event import ReferenceEvent
from app.db.session import async_session


class ReferencesRecorder:
    """
    Class to assist harvester with the recording in database of references logic
    """

    async def register(
            self,
            harvesting_id: int,
            new_ref: Reference,
            existing_references_source_identifiers: List[str],
            event_types: list[ReferenceEvent.Type] = None,
            history: bool = True,
    ) -> ReferenceEvent | None:
        """
        Register a new reference in the database

        :param harvesting_id: id of the harvesting to which the reference event is linked
        :param new_ref: reference to register
        :param event_types: list of event types to register
        :param existing_references_source_identifiers:
                list to register the source identifiers of the references that still exist,
                in case we return None, as we may need it to determine
                which references have been deleted
        :param history: whether to record the reference event in the harvesting history
        :return: the reference event
        """
        event_types = event_types_or_default(event_types)
        event_type = None
        ref = None
        if old_ref := await self.exists(new_ref):
            existing_references_source_identifiers.append(
                str(old_ref.source_identifier)
            )
            if old_ref.hash != new_ref.hash:
                if ReferenceEvent.Type.UPDATED.value not in event_types:
                    return None
                event_type = ReferenceEvent.Type.UPDATED
                new_ref.version = old_ref.version + 1
                await self._create_reference(new_ref)
                ref = new_ref
            else:
                if ReferenceEvent.Type.UNCHANGED.value not in event_types:
                    return None
                event_type = ReferenceEvent.Type.UNCHANGED
                ref = old_ref
        else:
            if ReferenceEvent.Type.CREATED.value not in event_types:
                return None
            event_type = ReferenceEvent.Type.CREATED
            await self._create_reference(new_ref)
            ref = new_ref
        async with async_session() as session:
            async with session.begin():
                return await ReferenceEventDAO(session).create_reference_event(
                    harvesting_id=harvesting_id,
                    reference=ref,
                    event_type=event_type,
                    history=history,
                )

    async def exists(self, new_ref: Reference) -> Reference | None:
        """
        Check if a reference already exists in the database
        :param new_ref: the new reference to compare with
        :return: the reference if it exists, None otherwise
        """
        async with async_session() as session:
            return await ReferenceDAO(session).get_last_reference_by_source_identifier(
                new_ref.source_identifier, new_ref.harvester
            )

    async def register_deletion(
            self, harvesting_id: int, old_ref: Reference, history: bool = True
    ) -> ReferenceEvent:
        """
        Register an event for a deleted reference

        :param harvesting_id: id of the harvesting during which the deletion occurred
        :param old_ref: the reference that was deleted
        :param history: whether to record the reference event in the harvesting history
        :return: the reference event related to the deletion
        """
        async with async_session() as session:
            async with session.begin():
                return await ReferenceEventDAO(session).create_reference_event(
                    harvesting_id=harvesting_id,
                    reference=old_ref,
                    event_type=ReferenceEvent.Type.DELETED,
                    history=history,
                )

    async def get_previous_references(
            self, entity_id: int, harvester: str
    ) -> ScalarResult[Reference]:
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
