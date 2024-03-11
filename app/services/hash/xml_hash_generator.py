from xml.etree.ElementTree import Element

from app.harvesters.xml_harvester_raw_result import XMLHarvesterRawResult

from app.services.hash.asbtract_hash_generator import AbstractHashGenerator
from app.services.hash.hash_key_xml import HashKeyXML


class XMLHashGenerator(AbstractHashGenerator):
    """
    Hash generator for XMLHarvesterRawResult
    """

    def hash_string(
        self, raw_data: XMLHarvesterRawResult, hash_keys: list[HashKeyXML]
    ) -> str:
        payload = raw_data.payload
        string_to_hash = ""
        for key in hash_keys:
            terms = [
                (node.text if node.text is not None else node)
                for node in payload.findall(f".//{key.value}", key.namespace)
            ]
            if key.sorted and terms:
                terms = self._sort_element(terms)
            string_to_hash += self._to_string(terms)

        return string_to_hash

    def _to_string(self, element: Element | str | list):
        if isinstance(element, str):
            return element
        if isinstance(element, list):
            return ";".join([self._to_string(e) for e in element])
        if element.text is not None:
            return element.text

        return ";".join([self._to_string(child) for child in element])

    def _sort_element(self, element: list[Element] | Element | str):
        if isinstance(element, str):
            return element
        if isinstance(element, list):
            return sorted([self._sort_element(e) for e in element])

        # If is an Element
        if element.text is not None:
            return element.text

        return ";".join(sorted([self._sort_element(child) for child in element]))
