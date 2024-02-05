from dataclasses import dataclass

from xml.etree import ElementTree
from app.harvesters.abstract_harvester_raw_result import AbstractHarvesterRawResult


@dataclass(kw_only=True)
class EtreeHarvesterRawResult(AbstractHarvesterRawResult[str, ElementTree]):
    """
    Raw result of an Harvester with identifier as a string and payload as an ElementTree
    """
