from sqlalchemy import select

from app.db.abstract_dao import AbstractDAO
from app.db.models.topic import Topic


class TopicDAO(AbstractDAO):
    """Data access object for topics."""

    async def get_topic_by_source_id(self, source_id: str) -> Topic | None:
        """Get a topic by its OpenAlex source identifier."""
        query = select(Topic).where(Topic.source_id == source_id)
        return await self.db_session.scalar(query)
