class DereferencingError(Exception):
    """
    Exception raised when a concept solver fails to dereference a concept
    URI due to an external endpoint failure.
    """

    def __init__(self, message: str) -> None:
        """Initialize the exception."""
        super().__init__(message)
