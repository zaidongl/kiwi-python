from behave import *
import logging

logger = logging.getLogger(__name__)

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



