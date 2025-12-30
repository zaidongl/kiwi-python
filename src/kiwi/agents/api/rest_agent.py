import logging
from typing import Dict, Optional, Any

import requests

from kiwi.agents.agent import Agent
from ...config.rest_agent_config import RestAgentConfig
from ...context.step_result import StepResult
from ...security.auth.BearerToken import BearerToken


class RestAgent(Agent):
    """
    REST API agent based on requests library to interact with RESTful services.
    """

    def __init__(self, agent_config: RestAgentConfig):
        super().__init__(agent_config.get_name())
        self._logger = logging.getLogger(__name__)
        self._agent_config = agent_config
        self._logger.info(f"Initialized RestAgent with config: {agent_config}")

    def send_request(self, method: str, endpoint: str, headers: Optional[Dict[str, str]] = None,
                     params: Optional[Dict[str, Any]] = None, body: Optional[Dict[str, Any]] = None) -> StepResult:
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
                    headers = {'Authorization': f'Bearer {auth}'}
