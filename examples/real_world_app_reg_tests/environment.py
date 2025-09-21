from behave import *

from kiwi.agents.AgentsManager import AgentsManager

def before_scenario(context, scenario):
    context.agents_manager = AgentsManager()