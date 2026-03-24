"""Import observation rows from JSONL for Braintrust datasets or local review."""

from __future__ import annotations

import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any, cast

from auto_prompt.evaluation.records import EvalRecord
from auto_prompt.evaluation.steps import StepId


def iter_observation_jsonl(path: Path) -> Iterator[EvalRecord]:
    """
    Yield :class:`~auto_prompt.evaluation.records.EvalRecord` objects from a JSONL file.

    Each line must be a JSON object with at least ``step_id``, ``run_id``, ``inputs``, ``outputs``.
    Optional keys: ``labels``, ``notes``, ``metadata``.

    :param path: Path to ``.jsonl``.
    :return: Iterator of records.
    :raises ValueError: On invalid JSON or missing required keys.
    """

    text = path.read_text(encoding="utf-8")
    for line_no, line in enumerate(text.splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            obj: dict[str, Any] = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{line_no}: invalid JSON") from exc
        _require_keys(obj, ("step_id", "run_id", "inputs", "outputs"), path, line_no)
        step_id_raw = obj["step_id"]
        if step_id_raw not in _STEP_SET:
            raise ValueError(f"{path}:{line_no}: invalid step_id {step_id_raw!r}")
        step_id = cast(StepId, step_id_raw)
        yield EvalRecord(
            step_id=step_id,
            run_id=str(obj["run_id"]),
            inputs=dict(obj["inputs"]),
            outputs=dict(obj["outputs"]),
            labels=dict(obj["labels"]) if obj.get("labels") is not None else None,
            notes=str(obj["notes"]) if obj.get("notes") is not None else None,
            metadata=dict(obj["metadata"]) if isinstance(obj.get("metadata"), dict) else {},
        )


_STEP_SET: frozenset[StepId] = frozenset(
    {
        "context_engineering",
        "scraper_markdown",
        "agent_turn",
        "end_to_end",
    },
)


def _require_keys(
    obj: dict[str, Any],
    keys: tuple[str, ...],
    path: Path,
    line_no: int,
) -> None:
    for key in keys:
        if key not in obj:
            raise ValueError(f"{path}:{line_no}: missing key {key!r}")
