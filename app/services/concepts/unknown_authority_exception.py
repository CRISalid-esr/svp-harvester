class UnknownAuthorityException(Exception):
    """Exception raised when the wonpt factory fails to infer authority from concept id"""

    def __init__(self, concept_id: str):
        self.concept_id = concept_id
        self.message = f"Could not infer authority from concept id {concept_id}"
        super().__init__(self.message)
