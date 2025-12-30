from ..auth.http_request_auth import HttpRequestAuth


class BearerToken(HttpRequestAuth):
    """
    Represents a Bearer Token for HTTP request authentication.
    """

    def __init__(self, token: str):
        super().__init__()
        self.token = token

    def get_auth(self) -> dict:
        """Return authentication headers as a dictionary."""
        return {'Authorization': f'Bearer {self.token}'}

    def get_token(self) -> str:
        """Return the bearer token."""
        return self.token

    def set_token(self, token: str):
        """Set a new bearer token."""
        self.token = token

    def __repr__(self):
        return f"BearerToken(token={self.token[:10]})" # Only show first 10 chars for security

    def __to_yaml__(self, dumper):
        return dumper.represent_dict({
            'token': self.token
        })

    @classmethod
    def __from_yaml__(cls, loader, node):
        data = loader.construct_mapping(node)
        return cls(data['token'])