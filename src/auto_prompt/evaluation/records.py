"""Structured rows passed to Braintrust or local eval fixtures."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from auto_prompt.evaluation.steps import StepId


@dataclass(slots=True)
class EvalRecord:
    """
    One eval row: inputs, outputs, and optional labels for a pipeline step.

    :param step_id: Logical step (see :data:`~auto_prompt.evaluation.steps.STEP_ORDER`).
    :param run_id: Correlation id for a single pipeline invocation.
    :param inputs: JSON-serializable inputs (paths, hashes, snippets).
    :param outputs: JSON-serializable outputs (artifact path, content hash, etc.).
    :param labels: Optional gold labels or human scores.
    :param notes: Free-form notes (e.g. from observation import).
    """

    step_id: StepId
    run_id: str
    inputs: dict[str, Any]
    outputs: dict[str, Any]
    labels: dict[str, Any] | None = None
    notes: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
