from sqlalchemy.orm import Session

from app.db.models import Retrieval


class RetrievalDAO:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    async def create_retrieval(self) -> Retrieval:
        new_retrieval = Retrieval()
        self.db_session.add(new_retrieval)
        await self.db_session.flush()
        return new_retrieval
