from dataclasses import dataclass

from app.harvesters.abstract_harvester_raw_result import AbstractHarvesterRawResult


@dataclass(kw_only=True)
class JsonHarvesterRawResult(AbstractHarvesterRawResult[str, dict]):
    """
    Raw result of an Harvester with identifier as a string and payload as a dict
    """
