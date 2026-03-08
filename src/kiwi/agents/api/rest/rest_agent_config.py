from kiwi.config.agent_config import AgentConfig
from kiwi.security.auth.http_request_auth import HttpRequestAuth

class RestAgentConfig(AgentConfig):
    def __init__(self, name: str, base_url: str, connection_timeout: int = 30000, request_auth: HttpRequestAuth = None,
                 headers: dict = None, cookies: dict = None, verify: bool = True):
        super().__init__(name)
        self.name = name
        self.base_url = base_url
        self.connection_timeout = connection_timeout
        self.request_auth = request_auth
        self.headers = headers if headers is not None else {}
        self.cookies = cookies if cookies is not None else {}
        self.verify = verify

    def get_name(self) -> str:
        return self.name

    def set_name(self, name: str):
        self.name = name

    def get_base_url(self) -> str:
        return self.base_url

    def set_base_url(self, base_url: str):
        self.base_url = base_url

    def get_connection_timeout(self) -> int:
        return self.connection_timeout

    def get_request_auth(self) -> HttpRequestAuth:
        return self.request_auth

    def get_headers(self) -> dict:
        return self.headers

    def get_cookies(self) -> dict:
        return self.cookies

    def get_verify(self) -> bool:
        return self.verify

    def __repr__(self):
        return f"RestAgentConfig(name={self.name}, base_url={self.base_url}, headers={self.headers})"

    def __to_yaml__(self, dumper):
        return dumper.represent_dict({
            'name': self.name,
            'base_url': self.base_url,
            'connection_timeout': self.connection_timeout,
            'request_auth': self.request_auth,
            'cookies': self.cookies,
            'verify': self.verify,
            'headers': self.headers
        })


    @classmethod
    def __from_yaml__(cls, loader, node):
        data = loader.construct_mapping(node)
        return cls(
            data['name'],
            data['base_url'],
            data.get('connection_timeout', 30000),
            data.get('request_auth'),
            data.get('headers', {}),
            data.get('cookies', {}),
            data.get('verify', True)
        )