import asyncio
import random

from pydantic import BaseModel

from app.harvesters.abstract_harvester import AbstractHarvester


class ScanrHarvester(AbstractHarvester):
    """
    Harvester for Scanr API
    """

    async def run(self) -> None:
        await asyncio.sleep(random.randint(1, 2) / 10)

    def is_relevant(self, entity: BaseModel) -> bool:
        return True

    async def fetch_results(self):
        yield
