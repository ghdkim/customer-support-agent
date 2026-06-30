from agents import Agent, RunContextWrapper

from models import UserAccountContext
from tools import (
    AgentToolUsageLoggingHooks,
    expedite_shipping,
    initiate_return_process,
    lookup_order_status,
    schedule_redelivery,
)


def dynamic_order_agent_instructions(
    wrapper: RunContextWrapper[UserAccountContext],
    agent: Agent[UserAccountContext],
) -> str:
    priority = " Apply premium shipping benefits." if wrapper.context.is_premium_customer() else ""
    return f"""
You are an Order Management specialist helping {wrapper.context.name}.
Customer tier: {wrapper.context.tier}.{priority}

Handle order status, tracking, delivery issues, redelivery, returns, exchanges,
and eligible shipping upgrades. Ask for an order or tracking number when needed,
then clearly state the status and next action.
"""


order_agent = Agent(
    name="Order Management Agent",
    handoff_description="Handles order status, shipping, delivery, tracking, and returns.",
    instructions=dynamic_order_agent_instructions,
    tools=[
        lookup_order_status,
        initiate_return_process,
        schedule_redelivery,
        expedite_shipping,
    ],
    hooks=AgentToolUsageLoggingHooks(),
)
