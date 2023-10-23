import asyncio
import random
from typing import AsyncGenerator, Type

from app.db.models.entity import Entity as DbEntity
from app.harvesters.abstract_harvester import AbstractHarvester
from app.harvesters.exceptions.external_endpoint_failure import ExternalEndpointFailure
from app.harvesters.json_harvester_raw_result import JsonHarvesterRawResult as RawResult


class ScanrHarvester(AbstractHarvester):
    """
    Harvester for Scanr API
    """

    async def fetch_results(self) -> AsyncGenerator[RawResult, None]:
        if random.randint(0, 2) == 1:
            raise ExternalEndpointFailure("Scanr API is down")
        await asyncio.sleep(random.randint(1, 20) / 10)

    def is_relevant(self, entity: Type[DbEntity]) -> bool:
        return False
