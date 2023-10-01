class UnexpectedFormatException(Exception):
    """Exception raised when a result fails to be parsed."""

    def __init__(self, message: str) -> None:
        """Initialize the exception."""
        super().__init__(message)
