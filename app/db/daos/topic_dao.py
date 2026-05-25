from sqlalchemy import select

from app.db.abstract_dao import AbstractDAO
from app.db.models.topic import Topic


class TopicDAO(AbstractDAO):
    async def get_topic_by_source_id(self, source_id: str) -> Topic | None:
        query = select(Topic).where(Topic.source_id == source_id)
        return await self.db_session.scalar(query)
