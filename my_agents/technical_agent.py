from agents import Agent, RunContextWrapper

from models import UserAccountContext
from output_guardrails import technical_output_guardrail
from tools import (
    AgentToolUsageLoggingHooks,
    escalate_to_engineering,
    provide_troubleshooting_steps,
    run_diagnostic_check,
)


def dynamic_technical_agent_instructions(
    wrapper: RunContextWrapper[UserAccountContext],
    agent: Agent[UserAccountContext],
) -> str:
    priority = " Offer priority escalation when appropriate." if wrapper.context.is_premium_customer() else ""
    return f"""
You are a Technical Support specialist helping {wrapper.context.name}.
Customer tier: {wrapper.context.tier}.{priority}

Diagnose product errors, crashes, setup problems, integrations, connectivity, and
performance issues. Gather the product name, exact error, environment, steps to
reproduce, and troubleshooting already attempted. Start with the simplest safe
steps, confirm results, and escalate unresolved issues when appropriate.
Do not perform billing, order, or account-management actions.
"""


technical_agent = Agent(
    name="Technical Support Agent",
    handoff_description="Handles troubleshooting, errors, setup, bugs, and product performance.",
    instructions=dynamic_technical_agent_instructions,
    tools=[
        run_diagnostic_check,
        provide_troubleshooting_steps,
        escalate_to_engineering,
    ],
    hooks=AgentToolUsageLoggingHooks(),
    output_guardrails=[technical_output_guardrail],
)
