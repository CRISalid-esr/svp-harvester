from pydantic import BaseModel

from app.harvesters.abstract_harvester import AbstractHarvester


class ScanrHarvester(AbstractHarvester):
    def relevant(self, entity: BaseModel) -> bool:
        pass
