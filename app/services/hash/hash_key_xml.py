from attr import dataclass

from app.services.hash.hash_key import HashKey


@dataclass
class HashKeyXML(HashKey):
    """
    HashKey dataclass for XMLHarvesterRawResult

    :namespace: The namespace of the XML
    """

    namespace: str = []
