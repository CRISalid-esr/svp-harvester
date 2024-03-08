from abc import ABC, abstractmethod

from app.harvesters.abstract_harvester_raw_result import (
    AbstractHarvesterRawResult,
)


class AbstractHashGenerator(ABC):
    """
    Abstract class for hashers
    """

    @abstractmethod
    def hash_string(self, raw_data: AbstractHarvesterRawResult, hash_keys: dict) -> str:
        """
        Generate the string to hash given payload using the provided hash dictionary.

        Args:
            payload (ResultTypeT): The payload to be hashed.
            hash_dict (dict): The hash dictionary containing the hashing algorithm and parameters.

        Returns:
            str: The hashed string.

        """
