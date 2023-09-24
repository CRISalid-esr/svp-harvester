import asyncio
import random

from pydantic import BaseModel

from app.harvesters.abstract_harvester import AbstractHarvester


class IdrefHarvester(AbstractHarvester):
    """
    Harvester for data.idref.fl
    """

    async def fetch_results(self):
        await asyncio.sleep(random.randint(1, 20) / 10)
        yield "end"

    def is_relevant(self, entity: BaseModel) -> bool:
        return True
