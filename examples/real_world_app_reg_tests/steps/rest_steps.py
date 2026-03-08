from behave import given, when, then
import logging
import json
from typing import Any

from kiwi.context.step_result import StepResult, StepResultStatus
from kiwi.context.scenario_context import ScenarioContext
from kiwi.exception.validation_error import ValidationError
from kiwi.utils.json_utils import JsonUtils
from kiwi.exception.path_error import PathError

logger = logging.getLogger(__name__)


@given('the REST API is configured with {rest_agent_name}')
def configure_rest_api(context, rest_agent_name):
    """Placeholder step to indicate REST API configuration. Agents are loaded from config."""
    logger.info("REST API configured with rest_agent_name")
    # Assuming agents are already loaded in scenario context from config
    context.scenario_context.get_agent(rest_agent_name)

def _get_last_response(context) -> Any:
    if not hasattr(context, 'scenario_context') or context.scenario_context is None:
        raise AssertionError("ScenarioContext is not available on context")
    step_result: StepResult = context.scenario_context.get_last_step_result()
    if step_result is None or step_result.data is None:
        raise AssertionError("No previous response available in scenario context")
    return step_result.data


def _resolve_variable(context, value: str):
    """Resolve a value that may reference a stored variable (starts with '@').
    Stored variables are kept as StepResult in ScenarioContext.variables; return their .data if so.
    """
    if not isinstance(value, str):
        return value
    if not value.startswith("@"):
        return value
    # If escaped @@ -> return with single @
    if value.startswith("@@"):
        return value[1:]
    # Otherwise try to find variable
    sc: ScenarioContext = context.scenario_context
    if sc.contains_variable(value):
        var = sc.get_variable(value)
        # var may be StepResult or raw; return data if StepResult
        if isinstance(var, StepResult):
            return var.data
        return var
    raise AssertionError(f"Variable {value} not found in scenario context")


@when('I send a {method} request to "{endpoint}"')
def send_request(context, method, endpoint):
    """Send an HTTP request using the configured agent. Optional request body can be provided
    in the step's docstring (context.text).
    """
    logger.info(f"Sending {method} request to {endpoint}")
    agent = context.scenario_context.get_current_agent()
    body = None
    if hasattr(context, 'text') and context.text and context.text.strip():
        # allow variable resolution in the body
        raw = context.text
        try:
            body_val = _resolve_variable(context, raw)
        except AssertionError:
            body_val = raw
        # if body_val is a dict/string etc, pass directly
        body = body_val
    # call agent send_request method
    result = agent.send_request(method=method, endpoint=endpoint, body=body)

    # wrap the response in StepResult
    step_result = StepResult(StepResultStatus.PASSED, f"{method} {endpoint}", result)

    # store last step result in scenario context
    context.scenario_context.set_last_step_result(step_result)
    # attach some log for reporting
    resp = result
    if resp is not None:
        context.scenario_context.write(f"Response ({getattr(resp, 'status_code', '')}): {resp.content}")


@then('the response status code should be {expected:d}')
def assert_status_code(context, expected):
    response = _get_last_response(context)
    actual = getattr(response, 'status_code', None)
    msg = f"Expected status code {expected} but got {actual}"
    if actual != expected:
        context.scenario_context.write(msg)
        raise AssertionError(msg)


@then('the response header "{header_name}" should contain "{expected}"')
def assert_header_contains(context, header_name, expected):
    response = _get_last_response(context)
    headers = getattr(response, 'headers', {}) or {}
    actual = headers.get(header_name)
    msg = f"Expected header '{header_name}' to contain '{expected}', actual='{actual}'"
    if actual is None or expected not in actual:
        context.scenario_context.write(msg)
        raise AssertionError(msg)


@then('the response header "{header_name}" should equal "{expected}"')
def assert_header_equals(context, header_name, expected):
    response = _get_last_response(context)
    headers = getattr(response, 'headers', {}) or {}
    actual = headers.get(header_name)
    msg = f"Expected header '{header_name}' to equal '{expected}', actual='{actual}'"
    if actual != expected:
        context.scenario_context.write(msg)
        raise AssertionError(msg)


@then('the response body should contain "{substring}"')
def assert_body_contains(context, substring):
    response = _get_last_response(context)
    text = None
    try:
        text = response.text
    except Exception:
        try:
            text = str(response)
        except Exception:
            text = ''
    msg = f"Expected response body to contain '{substring}'."
    if substring not in text:
        context.scenario_context.write(msg + f" Actual body: {text[:1000]}")
        raise AssertionError(msg + f" Actual body: {text[:1000]}")


@then('the JSON path "{json_path}" should equal "{expected}"')
def assert_json_path_equals(context, json_path, expected):
    response = _get_last_response(context)
    text = None
    try:
        text = response.text
    except Exception:
        text = None
    try:
        json_obj = JsonUtils.from_string(text)
    except ValueError:
        msg = "Response body is not valid JSON"
        context.scenario_context.write(msg)
        raise AssertionError(msg)
    try:
        val = JsonUtils.get(json_obj, json_path)
    except PathError:
        msg = f"JSON path '{json_path}' not found"
        context.scenario_context.write(msg)
        raise AssertionError(msg)
    # resolve expected variable reference
    try:
        expected_val = _resolve_variable(context, expected)
    except AssertionError:
        expected_val = expected
    # coerce both to string for comparison
    if isinstance(val, (dict, list)):
        actual_repr = json.dumps(val)
    else:
        actual_repr = str(val)
    if str(expected_val) != actual_repr:
        msg = f"JSON path '{json_path}' expected '{expected_val}' but was '{actual_repr}'"
        context.scenario_context.write(msg)
        raise AssertionError(msg)


@then('I save the JSON path "{json_path}" as "{var_name}"')
def save_json_path_as_variable(context, json_path, var_name):
    response = _get_last_response(context)
    text = None
    try:
        text = response.text
    except Exception:
        text = None
    try:
        json_obj = JsonUtils.from_string(text)
    except ValueError:
        msg = "Response body is not valid JSON"
        context.scenario_context.write(msg)
        raise AssertionError(msg)
    try:
        val = JsonUtils.get(json_obj, json_path)
    except PathError:
        msg = f"JSON path '{json_path}' not found"
        context.scenario_context.write(msg)
        raise AssertionError(msg)
    # store as StepResult for consistency with ScenarioContext variable usage
    sc: ScenarioContext = context.scenario_context
    sc.set_variable(var_name, StepResult(StepResultStatus.PASSED, message=f"Stored JSON path {json_path}", data=val))
    context.scenario_context.write(f"Saved JSON path '{json_path}' as variable '{var_name}': {val}")
