import logging

from kiwi.config.configurator import Configurator
from kiwi.agents.gui.playwright_agent import PlaywrightAgent
from kiwi.config.playwright_agent_config import PlaywrightAgentConfig
from ..config.rest_agent_config import RestAgentConfig

class AgentsManager:
    _logger = logging.getLogger(__name__)
    _instance = None
    _agents = {}

    def __new__(cls, *args, **kw):
        if cls._instance is None:
            cls._instance = object.__new__(cls, *args, **kw)
        return cls._instance

    def __init__(self):
        pass

    def get_agent(self, name: str):
        if name not in self._agents:
            configurator = Configurator()
            agent_config = configurator.get_config(name)
            self._logger.info(f"Got agent config: {agent_config}")

            if agent_config is None:
                raise Exception(f"Agent configuration for '{name}' not found.")
            if isinstance(agent_config, PlaywrightAgentConfig):
                self._agents[name] = PlaywrightAgent(agent_config)
            elif isinstance(agent_config, RestAgentConfig):
                self._agents[name] = RestAgentConfig(agent_config)
            else:
                raise Exception(f"Unsupported agent configuration type for '{name}'.")

        return self._agents.get(name)