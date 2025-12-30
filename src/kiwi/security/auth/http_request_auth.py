from abc import abstractmethod, ABC


class HttpRequestAuth(ABC):
    """
    Abstract base class for HTTP request authentication methods.
    """
    @abstractmethod
    def get_auth(self):
        pass