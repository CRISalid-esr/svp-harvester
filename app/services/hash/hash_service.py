import hashlib

from app.harvesters.abstract_harvester_raw_result import AbstractHarvesterRawResult
from app.harvesters.json_harvester_raw_result import JsonHarvesterRawResult
from app.harvesters.rdf_harvester_raw_result import RdfHarvesterRawResult
from app.harvesters.sparql_harvester_raw_result import SparqlHarvesterRawResult
from app.harvesters.xml_harvester_raw_result import XMLHarvesterRawResult
from app.services.hash.asbtract_hash_generator import AbstractHashGenerator
from app.services.hash.json_hash_generator import JsonHashGenerator
from app.services.hash.rdf_hash_generator import RdfHashGenerator
from app.services.hash.sparql_hash_generator import SparqlHashGenerator
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
        hash_generator = self._get_hash_generator(raw_data)
        hash_string = hash_generator.hash_string(raw_data, hash_dict)
        return hashlib.sha256(hash_string.encode("utf-8")).hexdigest()

    def _get_hash_generator(self, raw_data_class_name: str) -> AbstractHashGenerator:
        """
        Get the correct hasher for the raw data
        :param raw_data_class_name: the class name of the raw data
        :return: the correct hasher
        """
        if isinstance(raw_data_class_name, JsonHarvesterRawResult):
            return JsonHashGenerator()
        if isinstance(raw_data_class_name, XMLHarvesterRawResult):
            return XMLHashGenerator()
        if isinstance(raw_data_class_name, SparqlHarvesterRawResult):
            return SparqlHashGenerator()
        if isinstance(raw_data_class_name, RdfHarvesterRawResult):
            return RdfHashGenerator()

        raise ValueError(f"Hasher not found for {raw_data_class_name}")
