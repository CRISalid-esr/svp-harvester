import asyncio
import random

from pydantic import BaseModel

from app.harvesters.abstract_harvester import AbstractHarvester


class IdrefHarvester(AbstractHarvester):
    """
    Harvester for data.idref.fl
    """

    async def run(self) -> None:
        await asyncio.sleep(random.randint(1, 3) / 10)

    async def fetch_results(self):
        yield

    def is_relevant(self, entity: BaseModel) -> bool:
        return True
