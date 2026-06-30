from agents import (
    Agent,
    GuardrailFunctionOutput,
    RunContextWrapper,
    Runner,
    output_guardrail,
)

from models import TechnicalOutputGuardRailOutput, UserAccountContext


technical_output_guardrail_agent = Agent(
    name="Technical Support Output Guardrail",
    instructions="""
Review the technical-support response. Flag content that improperly handles:
- billing, payments, refunds, charges, or subscriptions;
- orders, shipping, tracking, delivery, or returns;
- account management, passwords, email changes, or account settings;
- unrelated topics outside technical troubleshooting.

A technical-support response may briefly recommend contacting another specialist,
but it must not perform that specialist's work.
""",
    output_type=TechnicalOutputGuardRailOutput,
)


@output_guardrail
async def technical_output_guardrail(
    wrapper: RunContextWrapper[UserAccountContext],
    agent: Agent[UserAccountContext],
    output: str,
) -> GuardrailFunctionOutput:
    result = await Runner.run(
        technical_output_guardrail_agent,
        output,
        context=wrapper.context,
    )
    validation = result.final_output
    triggered = (
        validation.contains_off_topic
        or validation.contains_billing_data
        or validation.contains_account_data
    )
    return GuardrailFunctionOutput(
        output_info=validation,
        tripwire_triggered=triggered,
    )
