class ValidationError(Exception):
    """Raised when a validation error occurs."""

    def __init__(self, message: str):
        super().__init__(message)