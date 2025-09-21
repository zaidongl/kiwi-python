import os
import unittest

from kiwi.config.configurator import Configurator


class TestConfigurator(unittest.TestCase):
    def test_load_config(self):
        os.environ.setdefault("KIWI_CONFIG_PATH", "./tests/test_data/config")
        configurator = Configurator()
        self.assertEqual("sample-test-project", configurator.get_test_project_name())  # add assertion here

    def test_load_agents_config(self):
        os.environ.setdefault("KIWI_CONFIG_PATH", "./tests/test_data/config")
        configurator = Configurator()
        agent_config = configurator.get_config("SampleBrowserAgent")
        self.assertIsNotNone(agent_config)
        self.assertEqual("chromium", agent_config.browser_type)

if __name__ == '__main__':
    unittest.main()
