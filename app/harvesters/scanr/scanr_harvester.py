import asyncio
import random

from pydantic import BaseModel

from app.harvesters.abstract_harvester import AbstractHarvester
from app.harvesters.exceptions.external_api_error import ExternalApiError


class ScanrHarvester(AbstractHarvester):
    """
    Harvester for Scanr API
    """

    async def fetch_results(self):
        if random.randint(0, 2) == 1:
            raise ExternalApiError("Scanr API is down")
        await asyncio.sleep(random.randint(1, 20) / 10)
        yield "end"

    def is_relevant(self, entity: BaseModel) -> bool:
        return True
