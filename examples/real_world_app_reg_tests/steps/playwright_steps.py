from behave import *

from kiwi.agents.AgentsManager import AgentsManager



@when("{agent_name} opens the page '{url}'")
def open_page(context, agent_name, url):
    print(f"Opening page {url} with agent {agent_name}")
    context.agents_manager.get_agent(agent_name).open_page(url)

@then("{agent_name} is on {page_name}")
def is_on_page(context, agent_name, page_name):
    # agents_manager = AgentsManager()
    context.agents_manager.get_agent(agent_name).is_on_page(page_name)

@when("{agent_name} type '{user_name}' into {user_textbox} and '{pwd}' into {pwd_textbox}")
def type_text(context, agent_name, user_name, user_textbox, pwd, pwd_textbox):
    # agents_manager = AgentsManager()
    context.agents_manager.get_agent(agent_name).type_text(user_textbox, user_name)
    context.agents_manager.get_agent(agent_name).type_text(pwd_textbox, pwd)

@then("{agent_name} clicks {element_name}")
def click_element(context, agent_name, element_name):
    # agents_manager = AgentsManager()
    context.agents_manager.get_agent(agent_name).click_element(element_name)



