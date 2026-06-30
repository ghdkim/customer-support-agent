from agents import Agent, RunContextWrapper

from models import UserAccountContext
from tools import (
    AgentToolUsageLoggingHooks,
    deactivate_account,
    enable_two_factor_auth,
    export_account_data,
    reset_user_password,
    update_account_email,
)


def dynamic_account_agent_instructions(
    wrapper: RunContextWrapper[UserAccountContext],
    agent: Agent[UserAccountContext],
) -> str:
    priority = " Mention priority service." if wrapper.context.is_premium_customer() else ""
    return f"""
You are an Account Management specialist helping {wrapper.context.name}.
Customer tier: {wrapper.context.tier}.{priority}

Handle login access, password resets, email changes, security settings, 2FA,
data exports, and account deactivation. Verify identity before sensitive changes.
Explain each action clearly and never request or expose a password, full payment
card number, authentication secret, or other unnecessary sensitive information.
"""


account_agent = Agent(
    name="Account Management Agent",
    handoff_description="Handles login, password, profile, security, and account settings.",
    instructions=dynamic_account_agent_instructions,
    tools=[
        reset_user_password,
        enable_two_factor_auth,
        update_account_email,
        deactivate_account,
        export_account_data,
    ],
    hooks=AgentToolUsageLoggingHooks(),
)
