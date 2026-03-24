"""Registered pipeline step identifiers for stepwise evaluation."""

from __future__ import annotations

from typing import Literal

StepId = Literal[
    "context_engineering",
    "scraper_markdown",
    "agent_turn",
    "end_to_end",
]

STEP_ORDER: tuple[StepId, ...] = (
    "context_engineering",
    "scraper_markdown",
    "agent_turn",
    "end_to_end",
)
