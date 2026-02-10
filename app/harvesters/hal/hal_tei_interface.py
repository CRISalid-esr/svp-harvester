from __future__ import annotations

from typing import List, Dict, Optional

from loguru import logger
from lxml import etree

from app.db.models.contributor_identifier import ContributorIdentifier


class HalTEIDecoder:
    """
    Wrapper for HAL API TEI (from "base_xml" field) to extract author identifiers.
    """

    TEI_NS = {"tei": "http://www.tei-c.org/ns/1.0"}

    _DISCARDED_TYPES = {"halauthorid"}

    _TYPE_MAP: Dict[str, str] = {
        # HAL TEI can sometimes expose these as uppercase values
        "GOOGLE SCHOLAR": ContributorIdentifier.IdentifierType.GOOGLE_SCHOLAR.value,
        "ORCID": ContributorIdentifier.IdentifierType.ORCID.value,
        "IDREF": ContributorIdentifier.IdentifierType.IDREF.value,
    }

    def __init__(self, tei_raw_data: str):
        self.tei_raw_data = tei_raw_data
        try:
            self.tree = etree.fromstring(tei_raw_data.encode("utf-8"))
        except etree.XMLSyntaxError as e:
            logger.error(f"TEI XML data are not usable: {e}")
            self.tree = None

    def get_identifiers(self, numeric_id_hal: int) -> List[Dict[str, str]]:
        """
        Given a numeric HAL ID, return a list of identifiers for that specific author.
        """
        identifiers: List[Dict[str, str]] = []

        if not self.tree:
            return identifiers

        xpath = (
            f"//tei:author[.//tei:idno[@type='idhal'][@notation='numeric' "
            f"and text()='{numeric_id_hal}']]"
        )
        author_elements = self.tree.xpath(xpath, namespaces=self.TEI_NS)
        if not author_elements:
            return identifiers

        author = author_elements[0]
        idnos = author.xpath(".//tei:idno", namespaces=self.TEI_NS)

        for idno in idnos:
            id_type = idno.get("type")
            id_value = (idno.text or "").strip()

            if not id_type or not id_value:
                continue

            identifier = self._process_identifier_data(id_type, id_value)
            if identifier is not None:
                identifiers.append(identifier)

        return identifiers

    def _process_identifier_data(
        self, id_type: str, id_value: str
    ) -> Optional[Dict[str, str]]:
        if id_type in self._DISCARDED_TYPES:
            return None

        if id_type == "idhal":
            normalized_type = (
                ContributorIdentifier.IdentifierType.IDHAL_I.value
                if id_value.isnumeric()
                else ContributorIdentifier.IdentifierType.IDHAL_S.value
            )
            return {"type": normalized_type, "value": id_value}

        mapped = self._TYPE_MAP.get(id_type)
        if mapped is not None:
            return {"type": mapped, "value": id_value}

        return {"type": self._normalize_unknown(id_type), "value": id_value}

    @staticmethod
    def _normalize_unknown(text: str) -> str:
        normalized = text.lower().replace(" ", "").replace("_", "")
        logger.warning(
            f"Unexpected identifier type '{text}' found in HAL TEI data. "
            f"It will be normalized to '{normalized}'"
        )
        return normalized
