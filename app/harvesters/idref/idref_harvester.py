import asyncio
import random

from pydantic import BaseModel

from app.harvesters.abstract_harvester import AbstractHarvester


class IdrefHarvester(AbstractHarvester):
    async def run(self, entity: BaseModel) -> None:
        await asyncio.sleep(random.randint(1, 10))

    def relevant(self, entity: BaseModel) -> bool:
        pass
