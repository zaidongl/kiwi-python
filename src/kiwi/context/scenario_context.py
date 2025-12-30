import logging
from typing import Dict

import allure
from behave.model import Scenario
from kiwi.agents.AgentsManager import AgentsManager
from kiwi.context.step_result import StepResult


class ScenarioContext(object):
    def __init__(self, scenario: Scenario):
        self.last_step_result = None
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

    def set_variable(self, name: str, value: StepResult):
        self.variables[name] = value

    def get_variable(self, name: str) -> StepResult:
        if name not in self.variables:
            raise KeyError(f"Variable '{name}' not found in scenario context.")
        return self.variables.get(name)

    def contains_variable(self, name: str) -> bool:
        return name in self.variables

    def set_last_step_result(self, step_result: StepResult):
        self.last_step_result = step_result

    def get_last_step_result(self) -> StepResult:
        return self.last_step_result