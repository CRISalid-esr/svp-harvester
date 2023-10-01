from app.db.models import Reference
from app.harvesters.abstract_harvester_raw_result import AbstractHarvesterRawResult
from app.harvesters.abstract_references_converter import AbstractReferencesConverter


class ScanrReferencesConverter(AbstractReferencesConverter):
    """
    Converts raw data from ScanR to a normalised Reference object
    """

    async def convert(self, raw_data: AbstractHarvesterRawResult) -> Reference:
        """
        Convert raw data from ScanR to a normalised Reference object
        :param raw_data: raw data from ScanR
        :return: Reference object
        """
