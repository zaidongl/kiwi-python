import asyncio
import os
import unittest

from kiwi.agents.AgentsManager import AgentsManager
from kiwi.agents.playwright_agent import PlaywrightAgent


class TestAgentsManager(unittest.TestCase):

    def test_get_agent(self):
        os.environ.setdefault("KIWI_CONFIG_PATH", "./tests/test_data/config")
        manager = AgentsManager()
        agent = manager.get_agent("SampleBrowserAgent")
        self.assertIsNotNone(agent)
        print(agent.__class__)
        self.assertTrue(isinstance(agent, PlaywrightAgent))


if __name__ == '__main__':
    unittest.main()
