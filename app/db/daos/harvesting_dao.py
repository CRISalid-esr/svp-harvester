from sqlalchemy import update, select
from sqlalchemy.orm import joinedload

from app.db.abstract_dao import AbstractDAO
from app.db.models.harvesting import Harvesting as DbHarvesting
from app.db.models.retrieval import Retrieval as DbRetrieval


class HarvestingDAO(AbstractDAO):
    """
    Data access object for Harvesting
    """

    async def create_harvesting(
            self,
            retrieval: DbRetrieval,
            harvester: str,
            state: DbHarvesting.State,
            history: bool = True
    ) -> DbHarvesting:
        """
        Create a harvesting for a retrieval

        :param state: state of the harvesting
        :param retrieval: retrieval to which the harvesting belongs
        :param harvester: type of harvester (idref, orcid, etc.)
        :param history: if True, the harvesting will be recorded in the history
        :return:
        """
        harvesting = DbHarvesting(harvester=harvester, state=state.value, history=history)
        harvesting.retrieval = retrieval
        self.db_session.add(harvesting)
        return harvesting

    async def get_harvesting_by_id(self, harvesting_id) -> DbHarvesting | None:
        """
        Get a harvesting by its id

        :param harvesting_id: id of the harvesting
        :return: the harvesting or None if not found
        """
        return await self.db_session.get(DbHarvesting, harvesting_id)

    async def get_harvesting_extended_info_by_id(
            self, harvesting_id
    ) -> DbHarvesting | None:
        """
        Get a harvesting without reference events but with retrieval and associated entity

        :param harvesting_id: id of the harvesting
        :return: the harvesting or None if not found
        """
        stmt = (
            select(DbHarvesting)
            .options(joinedload(DbHarvesting.retrieval))
            .where(DbHarvesting.id == harvesting_id)
        )
        return (await self.db_session.execute(stmt)).unique().scalar_one_or_none()

    async def update_harvesting_state(
            self, harvesting_id: int, state: DbHarvesting.State
    ):
        """
        Update the state of a harvesting

        :param harvesting_id: id of the harvesting
        :param state: new state
        :return: None
        """
        stmt = (
            update(DbHarvesting)
            .where(DbHarvesting.id == harvesting_id)
            .values({"state": state.value})
        )
        await self.db_session.execute(stmt)
