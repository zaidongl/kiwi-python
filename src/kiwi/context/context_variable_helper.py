import logging

from kiwi.context.step_result import StepResult
from kiwi.context.scenario_context import ScenarioContext

class ContextVariableHelper:
    """
    Helper class for managing context variables within a ScenarioContext.
    """

    _logger = logging.getLogger(__name__)

    @staticmethod
    def process_input_string(cls, context: ScenarioContext, input_string: str) -> StepResult | str:
        """
        Process the input string by replacing context variable placeholders with their actual values.

        Args:
            context: The ScenarioContext containing context variables.
            input_string: The input string potentially containing context variable placeholders.

        Returns:
            The processed string with context variable placeholders replaced by their values.
        """
        if context is None:
            ContextVariableHelper._logger.warning("ScenarioContext is None, cannot process input string.")
            return input_string
        if not input_string or not input_string.startswith("@"):
            return input_string
        elif input_string.strip().startswith("@@"):
            return input_string[1:]  # Escape sequence for '@'
        elif context.contains_variable(input_string):
            return context.get_variable(input_string)
        else:
            raise ValueError("No ")