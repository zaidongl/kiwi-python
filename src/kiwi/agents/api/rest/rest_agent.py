import logging
from typing import Dict, Optional, Any

import requests

from kiwi.agents.agent import Agent
from kiwi.agents.api.rest.rest_agent_config import RestAgentConfig
from kiwi.exception.argument_error import ArgumentError
from kiwi.security.auth.BearerToken import BearerToken
from kiwi.security.auth.basic_auth import BasicAuth


class RestAgent(Agent):
    """
    REST API agent based on requests library to interact with RESTful services.
    """
    _logger = logging.getLogger(__name__)

    def __init__(self, agent_config: RestAgentConfig):
        super().__init__(agent_config.get_name())
        self._agent_config = agent_config
        self._logger.info(f"Initialized RestAgent with config: {agent_config}")

    def send_request(self, method: str, endpoint: str, headers: Optional[Dict[str, str]] = None,
                     params: Optional[Dict[str, Any]] = None, body: Optional[Dict[str, Any]] = None) -> Optional[requests.Response]:
        """
        Send HTTP request using the specified method, headers, params and body to the given endpoint.
        Args:
        :param method: HTTP method (GET, POST, PUT, DELETE, etc.)
        :param endpoint: URL endpoint (will be appended to base_url)
        :param headers: Optional headers dictionary
        :param params: Optional query parameters dictionary
        :param body: Optional request body string
        :return: StepResult containing response data and step status
        """
        try:
            full_url = self._agent_config.get_base_url().strip() + endpoint.strip()
            request_kwargs = {
                'timeout': self._agent_config.get_connection_timeout() / 1000,  # convert ms to seconds
                'verify': self._agent_config.get_verify()
            }

            # Handle authentication
            if self._agent_config.get_request_auth() is not None:
                auth = self._agent_config.get_request_auth()
                if isinstance(auth, BearerToken):
                    headers = {'Authorization': f'Bearer {auth.get_token()}'}
                elif isinstance(auth, BasicAuth):
                    request_kwargs['auth'] = (auth.get_username(), auth.get_password())
                else:
                    self._logger.error(f"Unsupported authentication type: {type(auth)}")
                    raise ArgumentError(f"Unsupported authentication type: {type(auth)}")

            if self._agent_config.get_headers():
                if headers is None:
                    headers = {}
                headers.update(self._agent_config.get_headers())

            if headers:
                request_kwargs['headers'] = headers

            if params:
                request_kwargs['params'] = params

            if body:
                request_kwargs['data'] = body

            if self._agent_config.get_cookies():
                request_kwargs['cookies'] = self._agent_config.get_cookies()

            response = self._make_request(method.upper(), full_url, **request_kwargs)

            if response is None:
                self._logger.warning("No response received from the server.")
                return None

            self._logger.info(f"Received response: {response.status_code} - {response.text}")
            return response

        except ConnectionError as e:
            self._logger.error(f"ConnectionError during {method} request to {endpoint}: {e}")
            raise e
        except TimeoutError as e:
            self._logger.error(f"TimeoutError during {method} request to {endpoint}: {e}")
            raise e
        except Exception as e:
            self._logger.error(f"Exception during {method} request to {endpoint}: {e}")
            raise e

    def _make_request(self, method: str, url: str, **kwargs) -> Optional[requests.Response]:
        """
        Make the HTTP request based on method
        :param method:
        :param url:
        :param kwargs:
        :return:
        """
        session = requests.Session()

        try:
            if method == "GET":
                return session.get(url, **kwargs)
            elif method == "POST":
                return session.post(url, **kwargs)
            elif method == "PUT":
                return session.put(url, **kwargs)
            elif method == "DELETE":
                return session.delete(url, **kwargs)
            elif method == "PATCH":
                return session.patch(url, **kwargs)
            else:
                self._logger.error(f"Unsupported HTTP method: {method}")
                raise ArgumentError(f"Unsupported HTTP method: {method}")
        except Exception as e:
            self._logger.error(f"Error making {method} request to {url}: {e}")
            return None
