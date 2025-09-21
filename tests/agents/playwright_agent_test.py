import os
import unittest

from kiwi.agents.playwright_agent import PlaywrightAgent
from kiwi.config.playwright_agent_config import PlaywrightAgentConfig

class TestPlaywrightAgent(unittest.TestCase):
    def test_load_element_repo(self):
        os.environ.setdefault("KIWI_CONFIG_PATH", "./tests/test_data/config")
        agent_config = PlaywrightAgentConfig(name="test-agent", browser_type="chromium", headless=True, timeout=30000,
                                             element_repo="./tests/test_data/web-gui-repo/web-pages.yml")
        agent = PlaywrightAgent(agent_config=agent_config)
        self.assertEqual("#login_field", agent.element_repo.get("Login-Page.user-textbox"))

if __name__ == '__main__':
    unittest.main()
