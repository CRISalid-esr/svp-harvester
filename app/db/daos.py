from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Retrieval, Harvesting, Entity


class RetrievalDAO:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_retrieval(self, entity: Entity) -> Retrieval:
        retrieval = Retrieval()
        retrieval.entity = entity
        self.db_session.add(retrieval)
        await self.db_session.flush()
        return retrieval

    async def get_retrieval_by_id(self, retrieval_id: int) -> Retrieval | None:
        return await self.db_session.get(Retrieval, retrieval_id)


class HarvestingDAO:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_harvesting(
        self, retrieval: Retrieval, harvester: str
    ) -> Harvesting:
        harvesting = Harvesting(harvester=harvester)
        harvesting.retrieval = retrieval
        self.db_session.add(harvesting)
        await self.db_session.flush()
        return harvesting
