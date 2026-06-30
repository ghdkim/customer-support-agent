from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field


class UserAccountContext(BaseModel):
    """Application context shared with every support agent and tool."""

    customer_id: int
    name: str
    email: str
    tier: Literal["basic", "premium", "enterprise"] = "basic"
    troubleshooting_steps: list[str] = Field(default_factory=list)
    activity_log: list[str] = Field(default_factory=list)

    def is_premium_customer(self) -> bool:
        return self.tier in {"premium", "enterprise"}

    def add_troubleshooting_step(self, step: str) -> None:
        self.troubleshooting_steps.append(step)

    def log_activity(self, message: str) -> None:
        timestamp = datetime.now(timezone.utc).strftime("%H:%M:%S UTC")
        self.activity_log.append(f"{timestamp} — {message}")


class InputGuardrailOutput(BaseModel):
    is_off_topic: bool
    reason: str


class TechnicalOutputGuardRailOutput(BaseModel):
    contains_off_topic: bool
    contains_billing_data: bool
    contains_account_data: bool
    reason: str


class HandoffData(BaseModel):
    to_agent_name: str
    issue_type: str
    issue_description: str
    reason: str
