import os
import yaml

from kiwi.config.playwright_agent_config import PlaywrightAgentConfig

class Configurator(object):
    _instance = None
    _test_project_name = "test_project"
    _environment = "dev"
    _agent_configs = {}

    def __new__(cls, *args, **kw):
        if cls._instance is None:
            cls._instance = object.__new__(cls, *args, **kw)
        return cls._instance

    def __init__(self):
        configFolderPath = os.environ.get("KIWI_CONFIG_PATH", "./config")
        self.load_config(configFolderPath)

    def get_test_project_name(self) -> str:
        return self._test_project_name

    def get_environment(self) -> str:
        return self._environment

    def load_config(self, configFolderPath: str):
        print("Loading config from folder " + configFolderPath)
        with open(os.path.join(configFolderPath, "config.yml"), 'r') as root_config_file:
            root_config_yaml = yaml.load(root_config_file, Loader=yaml.FullLoader)
            self._test_project_name = root_config_yaml["test-project-name"]
            self._environment = root_config_yaml["environment"]

        # Load agents configuration
        agents_config_path = os.path.join(configFolderPath, self._environment, "agents.yml")
        self.load_agents_config(agents_config_path)

    def load_agents_config(self, configFilePath: str):
        yaml.add_representer(PlaywrightAgentConfig, PlaywrightAgentConfig.__to_yaml__)
        yaml.add_constructor('!PlaywrightAgentConfig', PlaywrightAgentConfig.__from_yaml__)

        with open(configFilePath, 'r') as file:
            data = yaml.load(file, Loader=yaml.FullLoader)
            print(data)

        for agent_config in data:
            self._agent_configs[agent_config.get_name()] = agent_config
            print(f"Loaded agent config: {agent_config}")
        print(f"Loaded {len(self._agent_configs)} agent configurations.")

    def get_config(self, name: str):
        return self._agent_configs.get(name, None)