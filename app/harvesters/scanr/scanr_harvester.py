import asyncio
import random
from asyncio import Queue

from pydantic import BaseModel

from app.harvesters.abstract_harvester import AbstractHarvester


class ScanrHarvester(AbstractHarvester):
    """
    Harvester for Scanr API
    """

    async def run(
        self, entity: BaseModel, harvesting_id: int, result_queue: Queue
    ) -> None:
        await asyncio.sleep(random.randint(1, 2) / 10)
        if result_queue:
            await result_queue.put(11)
        await asyncio.sleep(random.randint(1, 3) / 10)
        if result_queue:
            await result_queue.put(12)

    def is_relevant(self, entity: BaseModel) -> bool:
        return True
