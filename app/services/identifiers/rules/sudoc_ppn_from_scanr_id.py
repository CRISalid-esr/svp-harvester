import re
from loguru import logger

from app.db.models.reference import Reference
from app.db.models.reference_identifier import ReferenceIdentifier
from app.services.identifiers.identifier_inference_rule import IdentifierInferenceRule


class SudocPpnFromScanrIdRule(IdentifierInferenceRule):
    """
    Infer sudoc-ppn from ScanR source_identifier like: "sudoc258403519"
    """

    _pattern = re.compile(r"^sudoc(\d+)$", re.IGNORECASE)

    def infer(self, reference: Reference) -> None:
        if any(i.type == "sudoc-ppn" for i in reference.identifiers):
            return

        sid = getattr(reference, "source_identifier", None)
        if not isinstance(sid, str) or not sid:
            return

        match = self._pattern.match(sid.strip())
        if not match:
            return

        ppn = match.group(1)
        if not ppn:
            return

        reference.identifiers.append(ReferenceIdentifier(type="sudoc-ppn", value=ppn))

        logger.debug(f"Inferred sudoc-ppn={ppn} from ScanR id={sid}")
