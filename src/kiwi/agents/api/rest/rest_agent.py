import logging
from typing import Dict, Optional, Any, List

import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

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

            start_ts = time.perf_counter()
            response = self._make_request(method.upper(), full_url, **request_kwargs)
            elapsed_ms = int((time.perf_counter() - start_ts) * 1000)
            # Attach elapsed time to response for callers
            if response is not None:
                try:
                    setattr(response, 'kiwi_elapsed_ms', elapsed_ms)
                except Exception:
                    # ignore if attribute cannot be set
                    pass

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

    def send_requests_parallel(self, method: str, requests_data: List[Any], max_workers: int = 5) -> List[Optional[requests.Response]]:
        """
        Send multiple HTTP requests in parallel using threads.

        Args:
            method: HTTP method to use for all requests (GET, POST, ...)
            requests_data: A list where each item is either:
                - a string representing the endpoint (will be appended to base_url), or
                - a dict with keys: 'endpoint' (required), and optional 'headers', 'params', 'body'.
            max_workers: maximum number of threads to use.

        Returns:
            A list of requests.Response objects or None for requests that failed. The order of the
            returned list matches the order of the supplied requests_data.
        """
        if not requests_data:
            return []

        # Normalize inputs: convert simple endpoint strings to dicts
        normalized: List[Dict[str, Any]] = []
        for item in requests_data:
            if isinstance(item, str):
                normalized.append({'endpoint': item})
            elif isinstance(item, dict):
                if 'endpoint' not in item:
                    raise ArgumentError("Each request dict must include an 'endpoint' key")
                normalized.append(item)
            else:
                raise ArgumentError("requests_data items must be either endpoint strings or dicts")

        worker_count = max(1, min(len(normalized), int(max_workers)))
        self._logger.info(f"Starting parallel requests: method={method}, count={len(normalized)}, workers={worker_count}")

        results: List[Optional[requests.Response]] = [None] * len(normalized)

        def _worker(idx: int, req: Dict[str, Any]) -> None:
            try:
                endpoint = req.get('endpoint')
                headers = req.get('headers')
                params = req.get('params')
                body = req.get('body')
                self._logger.debug(f"Thread starting request idx={idx} endpoint={endpoint}")
                start_ts = time.perf_counter()
                resp = self.send_request(method, endpoint, headers=headers, params=params, body=body)
                elapsed_ms = int((time.perf_counter() - start_ts) * 1000)
                # ensure elapsed is available on the response object (overwrites if already set)
                if resp is not None:
                    try:
                        setattr(resp, 'kiwi_elapsed_ms', elapsed_ms)
                    except Exception:
                        pass
                results[idx] = resp
                self._logger.debug(f"Thread finished request idx={idx} status={(resp.status_code if resp is not None else None)} elapsed_ms={elapsed_ms}")
            except Exception as e:
                self._logger.error(f"Exception in parallel request idx={idx} endpoint={req.get('endpoint')}: {e}")
                results[idx] = None

        with ThreadPoolExecutor(max_workers=worker_count) as executor:
            futures = [executor.submit(_worker, idx, req) for idx, req in enumerate(normalized)]
            # Wait for all futures to complete and log exceptions if any
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    # Exceptions are already logged in _worker, but log here as well for visibility
                    self._logger.error(f"Unhandled exception in future: {e}")

        self._logger.info("Parallel requests completed")
        return results

