from agents import Agent, RunContextWrapper

from models import UserAccountContext
from tools import (
    AgentToolUsageLoggingHooks,
    apply_billing_credit,
    lookup_billing_history,
    process_refund_request,
    update_payment_method,
)


def dynamic_billing_agent_instructions(
    wrapper: RunContextWrapper[UserAccountContext],
    agent: Agent[UserAccountContext],
) -> str:
    priority = " Use priority processing." if wrapper.context.is_premium_customer() else ""
    return f"""
You are a Billing Support specialist helping {wrapper.context.name}.
Customer tier: {wrapper.context.tier}.{priority}

Handle payment failures, unexpected charges, invoices, subscription questions,
refunds, payment-method updates, and account credits. Explain charges clearly.
Never ask the customer to provide a complete card number, CVV, password, or
other sensitive credential in chat.
"""


billing_agent = Agent(
    name="Billing Support Agent",
    handoff_description="Handles payments, charges, refunds, invoices, and subscriptions.",
    instructions=dynamic_billing_agent_instructions,
    tools=[
        lookup_billing_history,
        process_refund_request,
        update_payment_method,
        apply_billing_credit,
    ],
    hooks=AgentToolUsageLoggingHooks(),
)
