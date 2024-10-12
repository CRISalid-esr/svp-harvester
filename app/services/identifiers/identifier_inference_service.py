from enum import Enum
from typing import List

from app.models.references import Reference
from app.services.identifiers.rules.hal_id_from_hal_url import HalIdFromHalUrlRule


class IdentifierInferenceService:
    """
    Service to infer missing identifiers for a reference
    """

    class Rule(Enum):
        HAL_ID_FROM_HAL_URL = HalIdFromHalUrlRule

    @classmethod
    def infer_identifiers(cls, reference: Reference, rules: List[Rule]) -> None:
        """
        Infer identifiers for a reference using a list of rules
        :param rules: the list of rules to use for inference
        :param reference: the reference to enrich with inferred identifiers
        :return: None
        """
        for rule in rules:
            # instantiate the rule and apply it to the reference
            rule.value().infer(reference)
