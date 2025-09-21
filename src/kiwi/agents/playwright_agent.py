import allure
from kiwi.agents.agent import Agent
from kiwi.config.playwright_agent_config import PlaywrightAgentConfig

from playwright.sync_api import sync_playwright
import yaml

class PlaywrightAgent(Agent):
    page = None

    def __init__(self, agent_config: PlaywrightAgentConfig):
        super().__init__(agent_config.name)
        self.config = agent_config
        self.element_repo = {}
        self._load_element_repo(self.config.element_repo)
        pw = sync_playwright().start()
        self.browser = pw.chromium.launch(headless=self.config.headless)
        self.context = self.browser.new_context(base_url=self.config.base_url)

    def reset(self):
        self.context.close()
        self.browser.close()
        pw = sync_playwright().start()
        self.browser = pw.chromium.launch(headless=self.config.headless)
        self.context = self.browser.new_context(base_url=self.config.base_url)

    def _load_element_repo(self, repo_file_path: str):
        with(open(repo_file_path, 'r')) as file:
            data = yaml.load(file, Loader=yaml.FullLoader)
            for page_name, elements in data.items():
                for element_name, selector in elements.items():
                    self.element_repo[f"{page_name}.{element_name}"] = selector
                    print(f"Loaded element: {page_name}.{element_name} -> {selector}")

    @classmethod
    def capture_screenshot(cls, page, name: str, timeout: int = 5000):
        if page is not None:
            file_path = f"screenshots/{name}.png"
            screenshot = page.screenshot(path=file_path, timeout=timeout)
            allure.attach(screenshot, name=name, attachment_type=allure.attachment_type.PNG)

    def open_page(self, url: str):
        self.reset()
        self.page = self.context.new_page()
        self.page.goto(url, timeout=self.config.timeout, wait_until="load")

    def is_on_page(self, selector: str):
        locator = self.element_repo.get(selector+".root")
        self.page.wait_for_selector(locator, timeout=self.config.timeout)
        PlaywrightAgent.capture_screenshot(page=self.page, name=selector, timeout=self.config.timeout)

    def close_page(self):
        if self.page is not None:
            self.page.close()

    def click_element(self, selector: str):
        locator = self.element_repo.get(selector)
        if self.page is not None:
            self.page.click(locator, timeout=self.config.timeout)
        else:
            raise Exception("No page is open. Please open a page before interacting with elements.")

    def type_text(self, selector: str, text: str):
        locator = self.element_repo.get(selector)
        if self.page is not None:
            self.page.fill(locator, text, timeout=self.config.timeout)
        else:
            raise Exception("No page is open. Please open a page before interacting with elements.")

