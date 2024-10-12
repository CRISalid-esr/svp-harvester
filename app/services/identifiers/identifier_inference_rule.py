from abc import ABC, abstractmethod

from app.models.references import Reference


class IdentifierInferenceRule(ABC):
    """
    Base class for identifier inference rules
    """

    @abstractmethod
    def infer(self, reference: Reference) -> None:
        """
        Infer identifiers for a reference
        """
        pass
