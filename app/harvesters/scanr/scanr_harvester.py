import asyncio
import random
from typing import Generator

from pydantic import BaseModel

from app.harvesters.abstract_harvester import AbstractHarvester
from app.harvesters.exceptions.external_endpoint_failure import ExternalEndpointFailure
from app.harvesters.json_harvester_raw_result import JsonHarvesterRawResult as RawResult


class ScanrHarvester(AbstractHarvester):
    """
    Harvester for Scanr API
    """

    async def fetch_results(self) -> Generator[RawResult, None, None]:
        if random.randint(0, 2) == 1:
            raise ExternalEndpointFailure("Scanr API is down")
        await asyncio.sleep(random.randint(1, 20) / 10)

    def is_relevant(self, entity: BaseModel) -> bool:
        return False
