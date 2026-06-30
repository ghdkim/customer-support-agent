from __future__ import annotations

import random
from datetime import datetime, timedelta

from agents import Agent, AgentHooks, RunContextWrapper, Tool, function_tool

from models import UserAccountContext


def _customer(ctx: RunContextWrapper[UserAccountContext]) -> UserAccountContext:
    return ctx.context


# =============================================================================
# TECHNICAL SUPPORT TOOLS
# =============================================================================


@function_tool
def run_diagnostic_check(
    ctx: RunContextWrapper[UserAccountContext],
    product_name: str,
    issue_description: str,
) -> str:
    """Run a simulated diagnostic check for a customer product."""
    diagnostics = [
        "✅ Server connectivity: Normal",
        "✅ API endpoints: Responsive",
        "⚠️ Cache memory: 85% full (clearing recommended)",
        "✅ Database connections: Stable",
        "⚠️ Product update: Available",
    ]
    _customer(ctx).log_activity(
        f"Ran diagnostics for {product_name}: {issue_description}"
    )
    return f"🔍 Diagnostic results for {product_name}:\n" + "\n".join(diagnostics)


@function_tool
def provide_troubleshooting_steps(
    ctx: RunContextWrapper[UserAccountContext], issue_type: str
) -> str:
    """Provide troubleshooting steps for a common issue category."""
    steps_map = {
        "connection": [
            "1. Confirm the device has a stable internet connection.",
            "2. Clear the browser cache and cookies.",
            "3. Temporarily disable browser extensions.",
            "4. Try a private or incognito browser window.",
            "5. Restart the router and device.",
        ],
        "login": [
            "1. Confirm the username or email address.",
            "2. Check that Caps Lock is disabled.",
            "3. Clear the browser cache.",
            "4. Request a password reset.",
            "5. Temporarily disable any VPN.",
        ],
        "performance": [
            "1. Close unnecessary tabs and applications.",
            "2. Clear cached application data.",
            "3. Check available memory and storage.",
            "4. Update the browser or application.",
            "5. Restart the application.",
        ],
        "crash": [
            "1. Install the latest application version.",
            "2. Restart the application and device.",
            "3. Confirm the device meets system requirements.",
            "4. Disable potentially conflicting software.",
            "5. Reproduce the issue and capture the error message.",
        ],
    }
    steps = steps_map.get(
        issue_type.lower(),
        [
            "1. Restart the application.",
            "2. Check for available updates.",
            "3. Record the exact error and steps that caused it.",
        ],
    )
    customer = _customer(ctx)
    customer.add_troubleshooting_step(
        f"Provided {issue_type.lower()} troubleshooting steps"
    )
    customer.log_activity(f"Provided troubleshooting for {issue_type}")
    return f"🛠️ Troubleshooting steps for {issue_type}:\n" + "\n".join(steps)


@function_tool
def escalate_to_engineering(
    ctx: RunContextWrapper[UserAccountContext],
    issue_summary: str,
    priority: str = "medium",
) -> str:
    """Create a simulated engineering escalation ticket."""
    customer = _customer(ctx)
    ticket_id = f"ENG-{random.randint(10000, 99999)}"
    customer.log_activity(f"Created engineering ticket {ticket_id}")
    expected_hours = 2 if customer.is_premium_customer() else 4
    return (
        "🚀 Issue escalated to Engineering\n"
        f"📋 Ticket ID: {ticket_id}\n"
        f"⚡ Priority: {priority.upper()}\n"
        f"📝 Summary: {issue_summary}\n"
        f"🕐 Expected initial response: {expected_hours} hours"
    )


# =============================================================================
# BILLING SUPPORT TOOLS
# =============================================================================


@function_tool
def lookup_billing_history(
    ctx: RunContextWrapper[UserAccountContext], months_back: int = 6
) -> str:
    """Return simulated billing history for the customer."""
    months_back = max(1, min(months_back, 12))
    payments = []
    for index in range(months_back):
        date = datetime.now() - timedelta(days=30 * index)
        amount = random.choice([29.99, 49.99, 99.99])
        status = random.choice(["Paid", "Paid", "Paid", "Failed"])
        payments.append(f"• {date:%b %Y}: ${amount:.2f} — {status}")
    _customer(ctx).log_activity(f"Viewed {months_back} months of billing history")
    return f"💳 Billing history (last {months_back} months):\n" + "\n".join(payments)


@function_tool
def process_refund_request(
    ctx: RunContextWrapper[UserAccountContext], refund_amount: float, reason: str
) -> str:
    """Create a simulated refund request."""
    customer = _customer(ctx)
    processing_days = 3 if customer.is_premium_customer() else 5
    refund_id = f"REF-{random.randint(100000, 999999)}"
    customer.log_activity(f"Created refund request {refund_id}")
    return (
        "✅ Refund request submitted\n"
        f"🔗 Refund ID: {refund_id}\n"
        f"💰 Amount: ${refund_amount:.2f}\n"
        f"📝 Reason: {reason}\n"
        f"⏱️ Estimated processing: {processing_days} business days"
    )


@function_tool
def update_payment_method(
    ctx: RunContextWrapper[UserAccountContext], payment_type: str
) -> str:
    """Create a simulated secure payment-method update request."""
    customer = _customer(ctx)
    customer.log_activity("Initiated payment-method update")
    return (
        "💳 Payment-method update initiated\n"
        f"📋 Type: {payment_type.replace('_', ' ').title()}\n"
        f"🔒 Secure instructions sent to: {customer.email}\n"
        "⏰ Link expires in 24 hours"
    )


@function_tool
def apply_billing_credit(
    ctx: RunContextWrapper[UserAccountContext], credit_amount: float, reason: str
) -> str:
    """Apply a simulated account credit."""
    customer = _customer(ctx)
    customer.log_activity(f"Applied ${credit_amount:.2f} billing credit")
    return (
        "🎁 Account credit applied\n"
        f"💰 Credit amount: ${credit_amount:.2f}\n"
        f"📝 Reason: {reason}\n"
        f"⚡ Account: {customer.customer_id}"
    )


# =============================================================================
# ORDER MANAGEMENT TOOLS
# =============================================================================


@function_tool
def lookup_order_status(
    ctx: RunContextWrapper[UserAccountContext], order_number: str
) -> str:
    """Return simulated order and delivery information."""
    customer = _customer(ctx)
    current_status = random.choice(["processing", "shipped", "in transit", "delivered"])
    tracking_number = f"1Z{random.randint(100000, 999999)}"
    estimated_delivery = datetime.now() + timedelta(days=random.randint(1, 5))
    customer.log_activity(f"Looked up order {order_number}")
    return (
        f"📦 Order: {order_number}\n"
        f"🏷️ Status: {current_status.title()}\n"
        f"🚚 Tracking: {tracking_number}\n"
        f"📅 Estimated delivery: {estimated_delivery:%B %d, %Y}"
    )


@function_tool
def initiate_return_process(
    ctx: RunContextWrapper[UserAccountContext],
    order_number: str,
    return_reason: str,
    items: str,
) -> str:
    """Start a simulated product return."""
    customer = _customer(ctx)
    return_id = f"RET-{random.randint(100000, 999999)}"
    fee = 0.0 if customer.is_premium_customer() else 5.99
    customer.log_activity(f"Started return {return_id} for order {order_number}")
    return (
        "📦 Return initiated\n"
        f"🔗 Return ID: {return_id}\n"
        f"📋 Order: {order_number}\n"
        f"📝 Items: {items}\n"
        f"💬 Reason: {return_reason}\n"
        f"💰 Return-label fee: ${fee:.2f}\n"
        f"📧 Instructions sent to: {customer.email}"
    )


@function_tool
def schedule_redelivery(
    ctx: RunContextWrapper[UserAccountContext],
    tracking_number: str,
    preferred_date: str,
) -> str:
    """Schedule a simulated package redelivery."""
    _customer(ctx).log_activity(f"Scheduled redelivery for {tracking_number}")
    return (
        "🚚 Redelivery scheduled\n"
        f"📦 Tracking: {tracking_number}\n"
        f"📅 Requested date: {preferred_date}"
    )


@function_tool
def expedite_shipping(
    ctx: RunContextWrapper[UserAccountContext], order_number: str
) -> str:
    """Expedite a simulated order for eligible customers."""
    customer = _customer(ctx)
    if not customer.is_premium_customer():
        return "❌ Expedited shipping is available to Premium and Enterprise customers."
    customer.log_activity(f"Expedited order {order_number}")
    return (
        "⚡ Shipping expedited\n"
        f"📦 Order: {order_number}\n"
        "🚀 Upgraded to next-day delivery\n"
        "💰 Additional charge: $0.00"
    )


# =============================================================================
# ACCOUNT MANAGEMENT TOOLS
# =============================================================================


@function_tool
def reset_user_password(
    ctx: RunContextWrapper[UserAccountContext], email: str
) -> str:
    """Send simulated password-reset instructions."""
    reset_token = f"RST-{random.randint(100000, 999999)}"
    _customer(ctx).log_activity("Initiated password reset")
    return (
        "🔐 Password reset initiated\n"
        f"📧 Reset link sent to: {email}\n"
        f"🔗 Demo reset token: {reset_token}\n"
        "⏰ Link expires in 1 hour"
    )


@function_tool
def enable_two_factor_auth(
    ctx: RunContextWrapper[UserAccountContext], method: str = "app"
) -> str:
    """Start simulated two-factor authentication setup."""
    customer = _customer(ctx)
    setup_code = f"2FA-{random.randint(100000, 999999)}"
    customer.log_activity(f"Started 2FA setup using {method}")
    return (
        "🔒 Two-factor authentication setup\n"
        f"📱 Method: {method.upper()}\n"
        f"🔑 Demo setup code: {setup_code}\n"
        f"📧 Instructions sent to: {customer.email}"
    )


@function_tool
def update_account_email(
    ctx: RunContextWrapper[UserAccountContext], old_email: str, new_email: str
) -> str:
    """Start a simulated account-email update."""
    verification_code = f"VER-{random.randint(100000, 999999)}"
    _customer(ctx).log_activity("Requested account-email change")
    return (
        "📧 Email update requested\n"
        f"📤 Current email: {old_email}\n"
        f"📥 New email: {new_email}\n"
        f"🔐 Demo verification code: {verification_code}\n"
        "⏰ Code expires in 30 minutes"
    )


@function_tool
def deactivate_account(
    ctx: RunContextWrapper[UserAccountContext], reason: str, feedback: str = ""
) -> str:
    """Create a simulated account-deactivation request."""
    customer = _customer(ctx)
    customer.log_activity("Initiated account deactivation")
    return (
        "⚠️ Account deactivation initiated\n"
        f"👤 Account: {customer.customer_id}\n"
        f"📝 Reason: {reason}\n"
        f"💬 Feedback: {feedback or 'None provided'}\n"
        "⏰ Scheduled within 24 hours"
    )


@function_tool
def export_account_data(
    ctx: RunContextWrapper[UserAccountContext], data_types: str
) -> str:
    """Create a simulated customer-data export request."""
    customer = _customer(ctx)
    export_id = f"EXP-{random.randint(100000, 999999)}"
    customer.log_activity(f"Requested data export {export_id}")
    return (
        "📊 Data export requested\n"
        f"🔗 Export ID: {export_id}\n"
        f"📋 Data types: {data_types}\n"
        f"📧 Download link will be sent to: {customer.email}"
    )


class AgentToolUsageLoggingHooks(AgentHooks[UserAccountContext]):
    """Store agent activity in context instead of writing UI from async hooks."""

    async def on_tool_start(
        self,
        context: RunContextWrapper[UserAccountContext],
        agent: Agent[UserAccountContext],
        tool: Tool,
    ) -> None:
        context.context.log_activity(f"{agent.name} started tool: {tool.name}")

    async def on_tool_end(
        self,
        context: RunContextWrapper[UserAccountContext],
        agent: Agent[UserAccountContext],
        tool: Tool,
        result: str,
    ) -> None:
        context.context.log_activity(f"{agent.name} completed tool: {tool.name}")

    async def on_handoff(
        self,
        context: RunContextWrapper[UserAccountContext],
        agent: Agent[UserAccountContext],
        source: Agent[UserAccountContext],
    ) -> None:
        context.context.log_activity(f"Handoff: {source.name} → {agent.name}")

    async def on_start(
        self,
        context: RunContextWrapper[UserAccountContext],
        agent: Agent[UserAccountContext],
    ) -> None:
        context.context.log_activity(f"Activated {agent.name}")

    async def on_end(
        self,
        context: RunContextWrapper[UserAccountContext],
        agent: Agent[UserAccountContext],
        output: object,
    ) -> None:
        context.context.log_activity(f"Completed {agent.name}")
