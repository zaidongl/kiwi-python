from behave import when, then
import logging
import json
from typing import Any

from kiwi.context.step_result import StepResult, StepResultStatus
from kiwi.context.scenario_context import ScenarioContext

logger = logging.getLogger(__name__)


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


def _parse_json_safe(text: str):
    try:
        return json.loads(text)
    except Exception:
        return None


def _get_json_path_value(json_obj: Any, path: str):
    """Simple JSON path resolver supporting paths like $.a.b[0].c or a.b.c or $.a[0].b
    This is a minimal helper (not full jsonpath support).
    """
    if path.startswith("$."):
        path = path[2:]
    if path.startswith("$"):
        path = path[1:]
    if path.startswith('.'):
        path = path[1:]
    if path == "" or path is None:
        return json_obj

    parts = []
    # split by dot but keep array indices
    raw_parts = path.split('.')
    for p in raw_parts:
        parts.append(p)

    current = json_obj
    for part in parts:
        if current is None:
            return None
        # handle array index like name[0]
        if '[' in part:
            # e.g. items[0][1]
            while '[' in part:
                idx_start = part.index('[')
                key = part[:idx_start]
                if key:
                    # descend into key
                    if isinstance(current, dict) and key in current:
                        current = current.get(key)
                    else:
                        return None
                # handle index
                idx_end = part.index(']')
                idx = part[idx_start+1:idx_end]
                try:
                    i = int(idx)
                except Exception:
                    return None
                if isinstance(current, list):
                    if i < 0 or i >= len(current):
                        return None
                    current = current[i]
                else:
                    return None
                part = part[idx_end+1:]
            # if there's any leftover name after indexes
            if part:
                if isinstance(current, dict) and part in current:
                    current = current.get(part)
                else:
                    return None
        else:
            # simple key
            if isinstance(current, dict):
                current = current.get(part)
            else:
                return None
    return current


@when('"{agent_name}" sends a {method} request to "{endpoint}"')
def send_request(context, agent_name, method, endpoint):
    """Send an HTTP request using the configured agent. Optional request body can be provided
    in the step's docstring (context.text).
    """
    logger.info(f"Sending {method} request to {endpoint} using agent {agent_name}")
    agent = context.scenario_context.get_agent(agent_name)
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
    # call agent methods (RestAgent has methods like get/post that return StepResult)
    method_upper = method.upper()
    if method_upper == 'GET':
        result = agent.get(endpoint)
    elif method_upper == 'POST':
        # if body is a string and looks like JSON, pass as body
        result = agent.post(endpoint, body=body)
    elif method_upper == 'PUT':
        result = agent.put(endpoint, body=body)
    elif method_upper == 'DELETE':
        result = agent.delete(endpoint)
    elif method_upper == 'PATCH':
        result = agent.patch(endpoint, body=body)
    else:
        raise AssertionError(f"Unsupported HTTP method: {method}")

    # store last step result in scenario context
    context.scenario_context.set_last_step_result(result)
    # attach some log for reporting
    try:
        resp = result.data
        if resp is not None:
            try:
                body_preview = resp.text[:2000]
            except Exception:
                body_preview = str(resp)
            context.scenario_context.write(f"Response ({getattr(resp, 'status_code', '')}): {body_preview}")
    except Exception:
        pass


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
    json_obj = _parse_json_safe(text)
    if json_obj is None:
        msg = "Response body is not valid JSON"
        context.scenario_context.write(msg)
        raise AssertionError(msg)
    val = _get_json_path_value(json_obj, json_path)
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
    json_obj = _parse_json_safe(text)
    if json_obj is None:
        msg = "Response body is not valid JSON"
        context.scenario_context.write(msg)
        raise AssertionError(msg)
    val = _get_json_path_value(json_obj, json_path)
    # store as StepResult for consistency with ScenarioContext variable usage
    sc: ScenarioContext = context.scenario_context
    sc.set_variable(var_name, StepResult(StepResultStatus.PASSED, message=f"Stored JSON path {json_path}", data=val))
    context.scenario_context.write(f"Saved JSON path '{json_path}' as variable '{var_name}': {val}")

