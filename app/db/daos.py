from sqlalchemy.orm import Session

from app.db.models import Retrieval, Harvesting


class RetrievalDAO:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    async def create_retrieval(self) -> Retrieval:
        retrieval = Retrieval()
        self.db_session.add(retrieval)
        await self.db_session.flush()
        return retrieval


class HarvestingDAO:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    async def create_harvesting(
        self, retrieval: Retrieval, harvester: str
    ) -> Harvesting:
        harvesting = Harvesting(harvester=harvester)
        harvesting.retrieval = retrieval
        self.db_session.add(harvesting)
        await self.db_session.flush()
        return harvesting
