import logging
from typing import Dict

import allure
from behave.model import Scenario
from kiwi.agents.AgentsManager import AgentsManager

class ScenarioContext(object):
    def __init__(self, scenario: Scenario):
        self.scenario = scenario
        self.agents_manager = AgentsManager()
        self.current_agent = None
        self.variables: Dict[str, StepResult] = {}
        self._logger = logging.Logger(__name__)

    def get_agent(self, name: str):
        self.current_agent = self.agents_manager.get_agent(name)
        return self.current_agent

    def get_current_agent(self):
        return self.current_agent

    def write(self, log: str):
        """write log to the scenario context for reporting"""
        self._logger.info(f"writing log: {log}")
        allure.attach(
            body=log,
            name="Log Output",
            attachment_type=allure.attachment_type.TEXT
        )