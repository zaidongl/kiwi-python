from kiwi.security.auth.http_request_auth import HttpRequestAuth
from kiwi.security.security_helper import SecurityHelper


class BasicAuth(HttpRequestAuth):
    """
    Basic Authentication for HTTP requests using username and password.
    """

    def __init__(self, username: str, password: str):
        super().__init__()
        self.username = username
        self.password = password

    def get_auth(self) -> dict:
        return {
            "username": self.username,
            "password": self.password
        }

    def get_username(self) -> str:
        return self.username

    def get_password(self) -> str:
        return self.password

    def set_username(self, username: str):
        self.username = username

    def set_password(self, password: str):
        self.password = password

    def __repr__(self):
        return f"BasicAuth(username={self.username}, password=****)"  # Hide password for security

    def __to_yaml__(self, dumper):
        return dumper.represent_dict({
            'username': self.username,
            'password': self.password
        })

    @classmethod
    def __from_yaml__(cls, loader, node):
        data = loader.construct_mapping(node)
        password = SecurityHelper.process_authentication_field(data['password'])
        return cls(data['username'], password)