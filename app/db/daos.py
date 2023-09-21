from sqlalchemy import select, update, Result, Row
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    Retrieval,
    Harvesting,
    Entity,
    State,
    Reference,
    ReferenceEvent,
    Concept,
    Label,
    Identifier,
)


class AbstractDAO:
    """
    Abstract data access object
    """

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session


class RetrievalDAO(AbstractDAO):
    """
    Data access object for Retrieval
    """

    async def create_retrieval(self, entity: Entity) -> Retrieval:
        """
        Create a retrieval for an entity we want to fetch references for

        :param entity: the entity we want to fetch references for
        :return: the created retrieval
        """
        retrieval = Retrieval()
        retrieval.entity = entity
        self.db_session.add(retrieval)
        await self.db_session.flush()
        return retrieval

    async def get_retrieval_by_id(self, retrieval_id: int) -> Retrieval | None:
        """
        Get a retrieval by its id

        :param retrieval_id: id of the retrieval
        :return: the retrieval or None if not found
        """
        return await self.db_session.get(Retrieval, retrieval_id)


class HarvestingDAO(AbstractDAO):
    """
    Data access object for Harvesting
    """

    async def create_harvesting(
            self, retrieval: Retrieval, harvester: str, state: State
    ) -> Harvesting:
        """
        Create a harvesting for a retrieval

        :param state: state of the harvesting
        :param retrieval: retrieval to which the harvesting belongs
        :param harvester: type of harvester (idref, orcid, etc.)
        :return:
        """
        harvesting = Harvesting(harvester=harvester, state=state.value)
        harvesting.retrieval = retrieval
        self.db_session.add(harvesting)
        return harvesting

    async def get_harvesting_by_id(self, harvesting_id) -> Harvesting | None:
        """
        Get a harvesting by its id

        :param harvesting_id: id of the harvesting
        :return: the harvesting or None if not found
        """
        return await self.db_session.get(Harvesting, harvesting_id)

    async def update_harvesting_state(self, harvesting_id: int, state: State):
        """
        Update the state of a harvesting

        :param harvesting_id: id of the harvesting
        :param state: new state
        :return: None
        """
        stmt = (
            update(Harvesting)
            .where(Harvesting.id == harvesting_id)
            .values({"state": state.value})
        )
        await self.db_session.execute(stmt)


class EntityDAO(AbstractDAO):
    """
    Data access object for abstract entities
    """

    async def get_entity_by_id(self, entity_id: int) -> Entity | None:
        """
        Get an entity by its id

        :param entity_id: id of the entity
        :return: the entity or None if not found
        """
        return await self.db_session.get(Entity, entity_id)


class ReferenceDAO(AbstractDAO):
    """
    Data access object for references
    """

    async def get_references_for_entity(self, entity_id: int) -> Result:
        """
        Get previously harvested references for an entity

        :param entity_id: id of the entity
        :return: list of references
        """
        query = (
            select(Reference)
            .join(ReferenceEvent)
            .join(Harvesting)
            .join(Retrieval)
            .where(Retrieval.entity_id == entity_id)
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


class ReferenceEventDAO:
    """
    Data access object for reference events
    """

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_reference_event(
            self,
            reference: Reference,
            harvesting: Harvesting,
            event_type: ReferenceEvent.Type,
    ) -> ReferenceEvent:
        """
        Create a reference event for a reference

        :param reference: reference to which the event is related
        :param harvesting: harvesting to which the event belongs
        :param event_type: state of the event
        :return: the created reference event
        """
        reference_event = ReferenceEvent(type=event_type.value)
        reference_event.reference = reference
        reference_event.harvesting = harvesting
        self.db_session.add(reference_event)
        return reference_event

    async def get_reference_event_by_id(
            self, reference_event_id: int
    ) -> ReferenceEvent | None:
        """
        Get a reference event by its id

        :param reference_event_id:
        :return:
        """
        return await self.db_session.get(ReferenceEvent, reference_event_id)


class ConceptDAO(AbstractDAO):
    """
    Data access object for concepts
    """

    async def get_concept_by_label_and_language(
            self, label: str, language: str
    ) -> Concept | None:
        """
        Get a concept by its label and language

        :param label: label of the concept
        :param language: language of the concept
        :return: the concept or None if not found
        """
        query = (
            select(Concept)
            .join(Label)
            .where(Label.value == label, Label.language == language)
        )
        return await self.db_session.scalar(query)


class IdentifierDAO(AbstractDAO):
    """
    Data access object for identifiers
    """

    async def get_identifier_and_entity_by_type_and_value(
            self, identifier_type: str, identifier_value: str
    ) -> Row[Identifier, Entity] | None:
        """
        Get an identifier (along with the associated entity) by its type and value

        :param identifier_type: type of the identifier
        :param identifier_value: value of the identifier
        :return: the identifier or None if not found
        """
        query = (
            select(Identifier, Entity)
            .join(Entity)
            .where(
                Identifier.type == identifier_type, Identifier.value == identifier_value
            )
        )

        return (await self.db_session.execute(query)).unique().first()
