import allure
from kiwi.agents.agent import Agent
from kiwi.config.playwright_agent_config import PlaywrightAgentConfig

from playwright.sync_api import sync_playwright, expect
import yaml
import logging

class PlaywrightAgent(Agent):
    def __init__(self, agent_config: PlaywrightAgentConfig):
        super().__init__(agent_config.name)
        self._logger = logging.getLogger(__name__)
        self.page = None
        self.config = agent_config
        self.element_repo = {}
        self._load_element_repo(self.config.element_repo)
        self.pw = sync_playwright().start()
        self.browser = self.pw.chromium.launch(headless=self.config.headless)
        self.context = self.browser.new_context(base_url=self.config.base_url)

    def reset(self):
        self._logger.info("Resetting PlaywrightAgent state.")
        self.context.close()
        self.browser.close()
        self.pw.stop()
        self.pw = sync_playwright().start()
        self.browser = self.pw.chromium.launch(headless=self.config.headless)
        self.context = self.browser.new_context(base_url=self.config.base_url)

    def _load_element_repo(self, repo_file_path: str):
        with(open(repo_file_path, 'r')) as file:
            data = yaml.load(file, Loader=yaml.FullLoader)
            for page_name, elements in data.items():
                for element_name, selector in elements.items():
                    self.element_repo[f"{page_name}.{element_name}"] = selector
                    self._logger.info(f"Loaded element: {page_name}.{element_name} -> {selector}")

    def get_locator(self, selector: str):
        locator = self.element_repo.get(selector)
        if locator is None:
            raise Exception(f"Locator for element '{selector}' not found in element repository.")
        return locator

    def capture_screenshot(self, name: str, timeout: int = 5000):
        if self.page is not None:
            file_path = f"screenshots/{name}.png"
            screenshot = self.page.screenshot(path=file_path, timeout=timeout)
            self._logger.info(f"Screenshot saved to {file_path}")
            allure.attach(screenshot, name=name, attachment_type=allure.attachment_type.PNG)
        else:
            raise Exception("No page is open. Please open a page before capturing a screenshot.")

    def open_page(self, url: str):
        self.reset()
        self.page = self.context.new_page()
        self.page.goto(url, timeout=self.config.timeout, wait_until="load")

    def is_on_page(self, selector: str):
        locator = self.get_locator(selector+".root")
        self.page.wait_for_selector(locator, timeout=self.config.timeout)

    def is_visible(self, selector: str):
        locator = self.get_locator(selector)
        expect(self.page.locator(locator)).to_be_visible(timeout=self.config.timeout)

    def close_page(self):
        if self.page is not None:
            self.page.close()

    def click_element(self, selector: str):
        locator = self.get_locator(selector)
        if self.page is not None:
            self.page.click(locator, timeout=self.config.timeout)
        else:
            raise Exception("No page is open. Please open a page before interacting with elements.")

    def type_text(self, selector: str, text: str):
        locator = self.get_locator(selector)
        if self.page is not None:
            self.page.fill(locator, text, timeout=self.config.timeout)
        else:
            raise Exception("No page is open. Please open a page before interacting with elements.")

    def see_text(self, selector: str, text: str):
        locator = self.get_locator(selector)
        if self.page is not None:
            expect(self.page.locator(locator)).to_have_text(text, timeout=self.config.timeout)
        else:
            raise Exception("No page is open. Please open a page before interacting with elements.")
