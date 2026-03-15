from behave import given, when, then
import logging

from kiwi.context.scenario_context import ScenarioContext
from kiwi.context.step_result import StepResult, StepResultStatus
from kiwi.agents.protocol.fix.fix_agent import FixAgent
from kiwi.agents.protocol.fix.fix_template import FixTemplate
import os
import json

logger = logging.getLogger(__name__)


@given('a FixAgent is created with sender "{sender}" and target "{target}" and version "{version}"')
def create_fix_agent(context, sender, target, version):
    agent = FixAgent(name='FixAgent', sender=sender, target=target, version=version)
    # store as current agent in scenario context
    if not hasattr(context, 'scenario_context') or context.scenario_context is None:
        raise AssertionError('ScenarioContext is not initialized')
    context.scenario_context.current_agent = agent
    context.scenario_context.write(f'Created FixAgent sender={sender} target={target} version={version}')


@given('FIX templates are loaded from "{relpath}"')
def load_fix_templates(context, relpath):
    sc: ScenarioContext = context.scenario_context
    path = relpath
    # allow relative paths from repo root
    if not os.path.isabs(path):
        path = os.path.join(os.getcwd(), relpath)
    tpl = FixTemplate()
    tpl.load_from_file(path)
    setattr(sc, 'fix_templates', tpl)
    sc.write(f'Loaded FIX templates from {path}')


@given('FIX templates are loaded')
def load_fix_templates_default(context):
    # default location relative to repo
    default_rel = 'examples/real_world_app_reg_tests/config/fix_template/fix_template.yaml'
    return load_fix_templates(context, default_rel)


@when('I build a FIX message of type "{msg_type}" with MsgSeqNum {seq_num:d} and fields:')
def build_fix_message(context, msg_type, seq_num):
    sc: ScenarioContext = context.scenario_context
    agent = sc.get_current_agent()
    if agent is None:
        raise AssertionError('No current FixAgent available')

    # context.table contains rows with 'tag' and 'value'
    body_fields = []
    for row in context.table:
        tag = int(row['tag'])
        val = row['value']
        body_fields.append((tag, val))

    raw_msg = agent.build_message(msg_type, body_fields=body_fields, seq_num=seq_num)

    # store as last step result
    step_result = StepResult(StepResultStatus.PASSED, f'Built FIX message type={msg_type}', raw_msg)
    sc.set_last_step_result(step_result)

    # attach raw message to report
    try:
        sc.attach_allure('FIX Message', raw_msg, as_json=False)
    except Exception:
        logger.debug('Failed to attach FIX message to report')


@when('I build a FIX message from template "{template_name}" with values:')
def build_fix_message_from_template(context, template_name):
    sc: ScenarioContext = context.scenario_context
    agent = sc.get_current_agent()
    if agent is None:
        raise AssertionError('No current FixAgent available')

    tpl: FixTemplate = getattr(sc, 'fix_templates', None)
    if tpl is None:
        # try default
        tpl = FixTemplate()
        default_path = os.path.join(os.getcwd(), 'examples/real_world_app_reg_tests/config/fix_template/fix_template.yaml')
        tpl.load_from_file(default_path)
        setattr(sc, 'fix_templates', tpl)

    # parse values table (columns: key, value)
    values = {}
    for row in context.table:
        key = row['key'] if 'key' in row.headings else row[0]
        raw = row['value'] if 'value' in row.headings else row[1]
        val = raw
        # try parse JSON for lists/dicts
        if isinstance(raw, str) and raw.strip().startswith(('[', '{')):
            try:
                val = json.loads(raw)
            except Exception:
                val = raw
        values[key] = val

    # Build flattened fields from template
    fields = tpl.build_fields(template_name, values)

    # determine msg_type (tag 35) from template header if present
    template = tpl.get_template(template_name)
    msg_type = None
    if template:
        header = template.get('header', []) or []
        for entry in header:
            if isinstance(entry, list) and len(entry) >= 2 and str(entry[0]) == '35':
                msg_type = str(entry[1])
                break
            if isinstance(entry, dict) and int(entry.get('tag', 0)) == 35:
                msg_type = entry.get('value')
                break

    if not msg_type:
        raise AssertionError('MsgType not found in template header; please specify')

    # allow seq_num and sending_time in values
    seq_num = values.get('seq_num') or values.get('MsgSeqNum') or values.get('34')
    try:
        seq_num = int(seq_num) if seq_num is not None else None
    except Exception:
        seq_num = None
    sending_time = values.get('sending_time') or values.get('52')

    raw_msg = agent.build_message(msg_type, body_fields=fields, seq_num=seq_num, sending_time=sending_time)

    step_result = StepResult(StepResultStatus.PASSED, f'Built FIX message from template={template_name}', raw_msg)
    sc.set_last_step_result(step_result)
    try:
        sc.attach_allure('FIX Message', raw_msg, as_json=False)
    except Exception:
        logger.debug('Failed to attach FIX message to report')


@then('the constructed FIX message should validate successfully')
def validate_fix_message(context):
    sc: ScenarioContext = context.scenario_context
    step_result: StepResult = sc.get_last_step_result()
    if step_result is None or step_result.data is None:
        raise AssertionError('No built FIX message available in scenario context')
    raw_msg = step_result.data
    agent = sc.get_current_agent()
    ok, err = agent.validate_message(raw_msg)
    if not ok:
        sc.write(f'FIX validation failed: {err}')
        raise AssertionError(f'FIX validation failed: {err}')


@then('the BodyLength and CheckSum fields should be correct')
def assert_bodylength_and_checksum(context):
    # This step duplicates validation but is kept explicit per scenario
    sc: ScenarioContext = context.scenario_context
    step_result: StepResult = sc.get_last_step_result()
    raw_msg = step_result.data
    agent = sc.get_current_agent()
    ok, err = agent.validate_message(raw_msg)
    if not ok:
        sc.write(f'BodyLength/CheckSum validation failed: {err}')
        raise AssertionError(f'BodyLength/CheckSum validation failed: {err}')
