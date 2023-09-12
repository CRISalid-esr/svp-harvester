import asyncio
import random
from asyncio import Queue

from pydantic import BaseModel

from app.harvesters.abstract_harvester import AbstractHarvester


class ScanrHarvester(AbstractHarvester):
    async def run(
        self, entity: BaseModel, harvesting_id: int, result_queue: Queue
    ) -> None:
        await asyncio.sleep(random.randint(1, 2) / 10)
        await result_queue.put(11) if result_queue else ...
        await asyncio.sleep(random.randint(1, 3) / 10)
        await result_queue.put(12) if result_queue else ...

    def is_relevant(self, entity: BaseModel) -> bool:
        return True
