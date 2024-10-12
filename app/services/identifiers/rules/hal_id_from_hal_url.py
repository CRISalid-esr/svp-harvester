import re
from urllib.parse import urlparse

from app.db.models.reference import Reference
from app.db.models.reference_identifier import ReferenceIdentifier
from app.services.identifiers.identifier_inference_rule import IdentifierInferenceRule


class HalIdFromHalUrlRule(IdentifierInferenceRule):
    """
    Rule to infer HAL identifier from HAL URL
    """

    def infer(self, reference: Reference) -> None:
        """
        Infer HAL identifier from HAL URL
        """
        if any(identifier.type == "hal" for identifier in reference.identifiers):
            return
        for manifestation in reference.manifestations:
            if hal_id := self.extract_hal_id(manifestation.page):
                reference.identifiers.append(
                    ReferenceIdentifier(type="hal", value=hal_id)
                )
                return

    @staticmethod
    def extract_hal_id(url: str | None) -> str | None:
        """
        Extract HAL identifier from HAL URL
        """
        if not url:
            return None
        parsed_url = urlparse(url)
        if not all([parsed_url.scheme, parsed_url.netloc]):
            return None
        if "hal." not in parsed_url.netloc:
            return None
        url_path = parsed_url.path.rstrip("/document")
        # e.g. 'https://shs.hal.science/halshs-02185511/file/Science%20paper%20ORI.pdf'
        url_path = re.sub(r"/file(/.*)?$", "", url_path)
        hal_id = url_path.split("/")[-1]
        if not re.match(r"hal[a-z]*-\d+(v\d+)?", hal_id):
            return None
        return hal_id
