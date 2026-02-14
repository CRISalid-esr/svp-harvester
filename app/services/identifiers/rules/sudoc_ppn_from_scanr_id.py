import re

from loguru import logger

from app.db.models.reference import Reference
from app.db.models.reference_identifier import ReferenceIdentifier
from app.services.identifiers.identifier_inference_rule import IdentifierInferenceRule


class SudocPpnFromScanrIdRule(IdentifierInferenceRule):
    """
    Infer ppn from ScanR source_identifier like:
    - sudoc258403519
    - sudoc12345678X
    """

    _pattern = re.compile(r"^sudoc(\d+[xX]?)$", re.IGNORECASE)

    def infer(self, reference: Reference) -> None:
        if any(
            i.type == ReferenceIdentifier.IdentifierType.PPN.value
            for i in reference.identifiers
        ):
            return

        source_identifier = reference.source_identifier
        if not isinstance(source_identifier, str) or not source_identifier:
            return

        match = self._pattern.match(source_identifier.strip())
        if not match:
            return

        ppn = match.group(1).upper()
        if not ppn:
            return

        reference.identifiers.append(
            ReferenceIdentifier(
                type=ReferenceIdentifier.IdentifierType.PPN.value, value=ppn
            )
        )

        logger.debug(f"Inferred ppn={ppn} from ScanR id={source_identifier}")
