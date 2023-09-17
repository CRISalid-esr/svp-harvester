from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Retrieval, Harvesting, Entity, State


class RetrievalDAO:
    """
    Data access object for Retrieval
    """

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

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


class HarvestingDAO:
    """
    Data access object for Harvesting
    """

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

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
        await self.db_session.commit()
        return harvesting

    async def get_harvesting_by_id(self, harvesting_id) -> Harvesting | None:
        """
        Get a harvesting by its id

        :param harvesting_id: id of the harvesting
        :return: the harvesting or None if not found
        """
        statement = select(Harvesting).where(Harvesting.id == harvesting_id)
        result = await self.db_session.scalar(statement)
        return result if result else None
