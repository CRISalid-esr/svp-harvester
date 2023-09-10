import asyncio
import random
from asyncio import Event, Queue

from pydantic import BaseModel

from app.harvesters.abstract_harvester import AbstractHarvester


class IdrefHarvester(AbstractHarvester):
    async def run(
        self, entity: BaseModel, harvesting_id: int, result_queue: Queue
    ) -> None:
        await asyncio.sleep(random.randint(1, 3) / 10)
        await result_queue.put(21) if result_queue else ...
        await asyncio.sleep(random.randint(1, 2) / 10)
        await result_queue.put(22) if result_queue else ...

    def relevant(self, entity: BaseModel) -> bool:
        pass
