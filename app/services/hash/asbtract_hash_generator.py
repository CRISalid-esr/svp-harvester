from abc import ABC, abstractmethod

from app.harvesters.abstract_harvester_raw_result import ResultTypeT


class AbstractHashGenerator(ABC):
    """
    Abstract class for hashers
    """

    @abstractmethod
    def hash_string(self, payload: ResultTypeT, hash_dict: dict) -> str:
        """
        Generate the string to hash given payload using the provided hash dictionary.

        Args:
            payload (ResultTypeT): The payload to be hashed.
            hash_dict (dict): The hash dictionary containing the hashing algorithm and parameters.

        Returns:
            str: The hashed string.

        """
        raise NotImplementedError
