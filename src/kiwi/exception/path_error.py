class PathError(Exception):
    """Raised when a specified path is not found in the data structure."""
    def __init__(self, message: str):
        super().__init__(message)