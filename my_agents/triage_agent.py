from agents import (
    Agent,
    GuardrailFunctionOutput,
    RunContextWrapper,
    Runner,
    handoff,
    input_guardrail,
)
from agents.extensions import handoff_filters
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX

from my_agents.account_agent import account_agent
from my_agents.billing_agent import billing_agent
from models import HandoffData, InputGuardrailOutput, UserAccountContext
from my_agents.order_agent import order_agent
from my_agents.technical_agent import technical_agent


input_guardrail_agent = Agent(
    name="Customer Support Input Guardrail",
    instructions="""
Determine whether the user's message concerns account management, billing,
orders, shipping, or technical support. Normal greetings and brief conversational
messages are allowed. Mark clearly unrelated requests as off-topic and explain why.
""",
    output_type=InputGuardrailOutput,
)


@input_guardrail
async def off_topic_guardrail(
    wrapper: RunContextWrapper[UserAccountContext],
    agent: Agent[UserAccountContext],
    input: str,
) -> GuardrailFunctionOutput:
    result = await Runner.run(
        input_guardrail_agent,
        input,
        context=wrapper.context,
    )
    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=result.final_output.is_off_topic,
    )


def dynamic_triage_agent_instructions(
    wrapper: RunContextWrapper[UserAccountContext],
    agent: Agent[UserAccountContext],
) -> str:
    return f"""
{RECOMMENDED_PROMPT_PREFIX}

Speak to the user in English and address them as {wrapper.context.name}.
You are the front-line customer-support triage agent for a
{wrapper.context.tier}-tier customer.

Classify the request into exactly one primary category:
- Technical Support: errors, bugs, crashes, setup, integrations, or performance.
- Billing Support: payments, charges, subscriptions, invoices, or refunds.
- Order Management: order status, tracking, shipping, delivery, or returns.
- Account Management: login, password, email, profile, security, or data export.

Ask one concise clarifying question only when the category is genuinely unclear.
Before handing off, briefly tell the customer which specialist will help and why.
For multiple issues, route the most urgent issue first and acknowledge the rest.
"""


def handle_handoff(
    wrapper: RunContextWrapper[UserAccountContext],
    input_data: HandoffData,
) -> None:
    wrapper.context.log_activity(
        f"Handoff to {input_data.to_agent_name}: {input_data.reason}"
    )


def make_handoff(agent: Agent[UserAccountContext]):
    return handoff(
        agent=agent,
        on_handoff=handle_handoff,
        input_type=HandoffData,
        input_filter=handoff_filters.remove_all_tools,
    )


triage_agent = Agent(
    name="Triage Agent",
    instructions=dynamic_triage_agent_instructions,
    input_guardrails=[off_topic_guardrail],
    handoffs=[
        make_handoff(account_agent),
        make_handoff(technical_agent),
        make_handoff(billing_agent),
        make_handoff(order_agent),
    ],
)
