class ArgumentError(Exception):
    """Raised when an argument is invalid."""
    def __init__(self, message: str):
        super().__init__(message)