import hashlib
from app.harvesters.abstract_harvester_raw_result import AbstractHarvesterRawResult
from app.services.hash.asbtract_hash_generator import AbstractHashGenerator
from app.services.hash.json_hash_generator import JsonHashGenerator
from app.services.hash.xml_hash_generator import XMLHashGenerator


class HashService:
    """
    HashService for get the hash from a RawResult
    Using the correct hasher
    """

    def hash(self, raw_data: AbstractHarvesterRawResult, hash_dict: dict):
        """
        Perform the hash with the correct hasher

        :param raw_data: the raw data
        :param hash_dict: the hash dict
        :return: the hash
        """
        hasher = self._get_hash_generator(raw_data.__class__.__name__)
        hash_string = hasher.hash_string(raw_data.payload, hash_dict)
        return hashlib.sha256(hash_string.encode("utf-8")).hexdigest()

    def _get_hash_generator(self, raw_data_class_name: str) -> AbstractHashGenerator:
        """
        Get the correct hasher for the raw data
        :param raw_data_class_name: the class name of the raw data
        :return: the correct hasher
        """
        if raw_data_class_name == "JsonHarvesterRawResult":
            return JsonHashGenerator()
        if raw_data_class_name == "XMLHarvesterRawResult":
            return XMLHashGenerator()
        # elif raw_data_class_name == "RdfRawResult":
        #     return RdfHasher()
        else:
            raise ValueError(f"Hasher not found for {raw_data_class_name}")
