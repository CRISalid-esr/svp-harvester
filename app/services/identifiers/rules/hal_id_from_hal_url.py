import re
from urllib.parse import urlparse

from loguru import logger

from app.db.models.reference import Reference
from app.db.models.reference_identifier import ReferenceIdentifier
from app.services.identifiers.identifier_inference_rule import IdentifierInferenceRule


class HalIdFromHalUrlRule(IdentifierInferenceRule):
    """
    Rule to infer HAL identifier from HAL URL
    """
    # TODO: EXPORT accepted_pattern
    accepted_patterns = ["hal", "halshs", "medihal", "inria", "acs", "sic", "tel", "jpa",
                         "dumas", "ineris", "in2p3", "inserm", "cea", "lirmm", "insu",
                         "pasteur"]

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
        match = re.match(fr"({'|'.join(HalIdFromHalUrlRule.accepted_patterns)})-\d+(v\d+)?", hal_id)
        if not match:
            logger.warning(f"Unknown HAL identifier pattern: {hal_id}")
            return None
        version = match.group(2)
        if version:
            hal_id = hal_id.removesuffix(version)
        return hal_id
