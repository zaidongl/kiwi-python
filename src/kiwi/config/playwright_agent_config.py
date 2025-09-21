from kiwi.config.agent_config import AgentConfig


class PlaywrightAgentConfig(AgentConfig):
    def __init__(self, name, browser_type='chromium', headless=True, timeout=3000, base_url=None,
                 element_repo='./web-gui-repo/web_pages.yml'):
        super().__init__(name)
        self.name = name
        self.browser_type = browser_type
        self.headless = headless
        self.timeout = timeout
        self.base_url = base_url
        self.element_repo = element_repo

    def get_name(self):
        return self.name

    def __repr__(self):
        return (f"PlaywrightAgentConfig(name={self.name}, browser_type={self.browser_type}, headless={self.headless}, "
                f"timeout={self.timeout}, base_url={self.base_url}, element_repo={self.element_repo})")

    def __to_yaml__(self, dumper):
        return dumper.represent_dict({'name': self.name,
                                      'browser_type': self.browser_type,
                                      'headless': self.headless,
                                      'timeout': self.timeout,
                                      'base_url': self.base_url,
                                      'element_repo': self.element_repo})

    @classmethod
    def __from_yaml__(cls, loader, node):
        data = loader.construct_mapping(node)
        return cls(data['name'], data.get('browser_type', 'chromium'), data.get('headless', True),
                   data.get('timeout', 3000), data.get('base_url'), data.get('element_repo', './web-gui-repo/web_pages.yml'))