from app.harvesters.xml_harvester_raw_result import XMLHarvesterRawResult

from app.services.hash.asbtract_hash_generator import AbstractHashGenerator
from app.services.hash.hash_key import HashKey


class XMLHashGenerator(AbstractHashGenerator):
    """ "
    Hash generator for XMLHarvesterRawResult
    """

    NAMESPACE = {
        "dc": "http://purl.org/dc/elements/1.1/",
        "dcterms": "http://purl.org/dc/terms/",
        "oai": "http://www.openarchives.org/OAI/2.0/",
        "qdc": "http://www.bl.uk/namespaces/oai_dcq/",
    }

    def hash_string(
        self, raw_data: XMLHarvesterRawResult, hash_keys: list[HashKey]
    ) -> str:
        payload = raw_data.payload
        string_to_hash = ""
        for key in hash_keys:
            terms = [
                node.text for node in payload.findall(f".//{key.value}", self.NAMESPACE)
            ]
            if key.sorted:
                terms.sort()
            string_to_hash += ";".join(terms)

        return string_to_hash
