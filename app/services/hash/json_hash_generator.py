import json
from typing import Any
from app.harvesters.json_harvester_raw_result import JsonHarvesterRawResult

from app.services.hash.asbtract_hash_generator import AbstractHashGenerator


class JsonHashGenerator(AbstractHashGenerator):
    """
    Hasher for JsonHarvesterRawResult
    """

    def hash_string(self, raw_data: JsonHarvesterRawResult, hash_keys: dict) -> str:
        """
        Hashes the values of the payload dictionary based on the keys specified in the hash_dict.

        Args:
            payload (dict): The dictionary containing the payload data.
            hash_dict (dict): The dictionary specifying the keys to be hashed.

        Returns:
            str: The hashed string generated from the values of the payload dictionary.

        """
        payload = raw_data.payload
        hash_string = ""
        for key in hash_keys:
            obj = payload.get(key, "")
            obj_sorted = self._sort_element(obj)
            hash_string += str(obj_sorted)

        return hash_string

    def _sort_element(self, obj: Any):
        if isinstance(obj, str):
            return obj
        if isinstance(obj, list):
            return sorted([self._sort_element(o) for o in obj])
        if isinstance(obj, dict):
            return json.dumps(
                {k: self._sort_element(v) for k, v in obj.items()}, sort_keys=True
            )
        return str(obj)
