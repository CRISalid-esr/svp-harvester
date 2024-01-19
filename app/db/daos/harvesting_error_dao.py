from sqlalchemy import insert
from app.db.abstract_dao import AbstractDAO
from app.db.models.harvesting_error import HarvestingError


class HarvestingErrorDAO(AbstractDAO):
    """
    Data access object for HarvestingError
    """

    async def add_harvesting_error(self, harvesting_id: int, error: Exception):
        """
        Add a harvesting error
        """
        stmt = insert(HarvestingError).values(
            harvesting_id=harvesting_id, name=type(error).__name__, message=str(error)
        )
        await self.db_session.execute(stmt)
