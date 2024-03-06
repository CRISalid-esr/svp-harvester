from xml.etree import ElementTree

from app.services.hash.asbtract_hash_generator import AbstractHashGenerator


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

    def hash_string(self, payload: ElementTree, hash_keys: dict) -> str:
        string_to_hash = ""
        for key in hash_keys:
            a = sorted(
                [node.text for node in payload.findall(f".//{key}", self.NAMESPACE)]
            )
            string_to_hash += ";".join(a)

        return string_to_hash
