from behave import *
import logging

from playwright.sync_api import expect

from kiwi.context.step_result import StepResult

logger = logging.getLogger(__name__)

def login(context, agent_name, user_name, pwd):
    logger.info(f"Login the web site")
    agent = context.scenario_context.get_agent(agent_name)


@when('"{agent_name}" opens the page "{url}"')
def open_page(context, agent_name, url):
    logger.info(f"Opening page {url} with agent {agent_name}")
    context.scenario_context.get_agent(agent_name).open_page(url)

@then('"{agent_name}" is on "{page_name}"')
def is_on_page(context, agent_name, page_name):
    context.scenario_context.get_agent(agent_name).is_on_page(page_name)

@when('"{agent_name}" type "{user_name}" into "{user_textbox}" and "{pwd}" into "{pwd_textbox}"')
def type_text(context, agent_name, user_name, user_textbox, pwd, pwd_textbox):
    context.scenario_context.get_agent(agent_name).type_text(user_textbox, user_name)
    context.scenario_context.get_agent(agent_name).type_text(pwd_textbox, pwd)

@then('"{agent_name}" clicks "{element_name}"')
def click_element(context, agent_name, element_name):
    context.scenario_context.get_agent(agent_name).click_element(element_name)

@then('"{agent_name}" sees "{text}" on "{element_name}"')
def see_element(context, agent_name, text, element_name):
    context.scenario_context.get_agent(agent_name).is_visible(element_name)
    context.scenario_context.get_agent(agent_name).see_text(element_name, text)

@then('"{agent_name}" sees {count:d} "{element_name}" in {duration:d} milliseconds')
def see_element_in_timeout(context, agent_name, count, element_name, duration):
    agent = context.scenario_context.get_agent(agent_name)
    page = agent.get_page()
    element_locator = agent.get_locator(element_name)
    expect(page.locator(element_locator)).to_have_count(count, timeout=duration)

@when('"{agent_name}" type "{text}" into textbox "{textbox}"')
def type_text_into_textbox(context, agent_name, text, textbox):
    agent = context.scenario_context.get_agent(agent_name)
    page = agent.get_page()
    page.locator(agent.get_locator(textbox)).focus()
    processed_text = ContextVariableHelper.process_input_string(context.scenario_context, text)
    if isinstance(processed_text, StepResult):
        processed_text = processed_text.data

    agent.type_text(textbox, processed_text)



