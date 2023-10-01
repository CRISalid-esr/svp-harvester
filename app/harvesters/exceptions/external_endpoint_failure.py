class ExternalEndpointFailure(Exception):
    """Exception raised when an external API call fails."""

    def __init__(self, message: str) -> None:
        """Initialize the exception."""
        super().__init__(message)
