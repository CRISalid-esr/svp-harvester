from sqlalchemy import update

from app.db.abstract_dao import AbstractDAO
from app.db.models.harvesting import Harvesting
from app.db.models.retrieval import Retrieval


class HarvestingDAO(AbstractDAO):
    """
    Data access object for Harvesting
    """

    async def create_harvesting(
            self, retrieval: Retrieval, harvester: str, state: Harvesting.State
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

    async def update_harvesting_state(self, harvesting_id: int, state: Harvesting.State):
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
