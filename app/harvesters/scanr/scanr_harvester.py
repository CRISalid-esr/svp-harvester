import asyncio
import random

from pydantic import BaseModel

from app.harvesters.abstract_harvester import AbstractHarvester


class ScanrHarvester(AbstractHarvester):
    async def run(self, entity: BaseModel, harvesting_id: int) -> None:
        await asyncio.sleep(random.randint(1, 10))

    def relevant(self, entity: BaseModel) -> bool:
        pass
