import logging
from uuid import uuid4

from behave.model import Step
from behave.runner import Context
from kiwi.context.scenario_context import ScenarioContext
from kiwi.agents.playwright_agent import PlaywrightAgent

logger = logging.getLogger(__name__)

def before_scenario(context, scenario):
    logger.info("Before scenario setup")
    if not hasattr(context, 'scenario_context'):
        context.scenario_context = ScenarioContext(scenario=scenario)

def after_step(context: Context, step: Step):
    if step.status.is_failure() or step.status.is_error():
        logger.info("Step failed or has error, capturing screenshot")
        unique_id = uuid4()
        current_agent = context.scenario_context.get_current_agent()
        if isinstance(current_agent, PlaywrightAgent):
            current_agent.capture_screenshot(name=f"{unique_id.hex}_failure")
        else:
            logger.warning("Current agent is not a PlaywrightAgent, cannot capture screenshot")