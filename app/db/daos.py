from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Retrieval, Harvesting, Entity


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
        self, retrieval: Retrieval, harvester: str
    ) -> Harvesting:
        """
        Create a harvesting for a retrieval

        :param retrieval: retrieval to which the harvesting belongs
        :param harvester: type of harvester (idref, orcid, etc.)
        :return:
        """
        harvesting = Harvesting(harvester=harvester)
        harvesting.retrieval = retrieval
        self.db_session.add(harvesting)
        await self.db_session.flush()
        return harvesting
