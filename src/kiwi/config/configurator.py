import os
import yaml
import logging

from kiwi.config.playwright_agent_config import PlaywrightAgentConfig

class Configurator(object):
    _logger = logging.getLogger(__name__)
    _instance = None
    _test_project_name = "test_project"
    _environment = "dev"
    _agent_configs = {}

    def __new__(cls, *args, **kw):
        if cls._instance is None:
            cls._instance = object.__new__(cls, *args, **kw)
        return cls._instance

    def __init__(self):
        config_folder_path = os.environ.get("KIWI_CONFIG_PATH", "./config")
        self.load_config(config_folder_path)

    def get_test_project_name(self) -> str:
        return self._test_project_name

    def get_environment(self) -> str:
        return self._environment

    def load_config(self, config_folder_path: str):
        self._logger.info("Loading config from folder " + config_folder_path)
        with open(os.path.join(config_folder_path, "config.yml"), 'r') as root_config_file:
            root_config_yaml = yaml.load(root_config_file, Loader=yaml.FullLoader)
            self._test_project_name = root_config_yaml["test-project-name"]
            self._environment = root_config_yaml["environment"]

        # Load agents configuration
        agents_config_path = os.path.join(config_folder_path, self._environment, "agents.yml")
        self.load_agents_config(agents_config_path)

    def load_agents_config(self, config_file_path: str):
        yaml.add_representer(PlaywrightAgentConfig, PlaywrightAgentConfig.__to_yaml__)
        yaml.add_constructor('!PlaywrightAgentConfig', PlaywrightAgentConfig.__from_yaml__)

        with open(config_file_path, 'r') as file:
            data = yaml.load(file, Loader=yaml.FullLoader)
            print(data)

        for agent_config in data:
            self._agent_configs[agent_config.get_name()] = agent_config
            self._logger.info(f"Loaded agent config: {agent_config}")
        self._logger.info(f"Loaded {len(self._agent_configs)} agent configurations.")

    def get_config(self, name: str):
        return self._agent_configs.get(name, None)