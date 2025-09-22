from behave.model import Scenario
from kiwi.agents.AgentsManager import AgentsManager

class ScenarioContext(object):
    def __init__(self, scenario: Scenario):
        self.scenario = scenario
        self.agents_manager = AgentsManager()
        self.current_agent = None

    def get_agent(self, name: str):
        self.current_agent = self.agents_manager.get_agent(name)
        return self.current_agent

    def get_current_agent(self):
        return self.current_agent