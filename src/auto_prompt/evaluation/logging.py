"""Log pipeline steps to Braintrust via the official SDK."""

from __future__ import annotations

import hashlib
import uuid
from typing import Any

from braintrust import init_logger

from auto_prompt.errors import ConfigurationError, DependencyUnavailableError
from auto_prompt.evaluation.config import BraintrustConfig, load_braintrust_config_from_env
from auto_prompt.evaluation.records import EvalRecord
from auto_prompt.evaluation.steps import StepId


def log_step(
    record: EvalRecord,
    *,
    config: BraintrustConfig | None = None,
) -> None:
    """
    Dispatch a single :class:`~auto_prompt.evaluation.records.EvalRecord` to Braintrust.

    Currently supports ``context_engineering``; other step ids raise ``ConfigurationError``.

    :param record: Row to log.
    :param config: Optional config; defaults to env via :func:`load_braintrust_config_from_env`.
    :return: None.
    :raises ConfigurationError: Unknown step or missing config when needed.
    :raises DependencyUnavailableError: Braintrust client or network failure.
    """

    cfg = config if config is not None else load_braintrust_config_from_env()
    if record.step_id == "context_engineering":
        _log_context_engineering(record, cfg)
        return
    raise ConfigurationError(f"Unsupported step_id for logging: {record.step_id!r}")


def _log_context_engineering(record: EvalRecord, config: BraintrustConfig) -> None:
    """Emit a span under a Braintrust project logger."""

    try:
        logger = init_logger(
            project=config.project_name,
            project_id=config.project_id,
            api_key=config.api_key,
            set_current=False,
        )
        name = f"context_engineering:{record.run_id}"
        meta: dict[str, Any] = dict(record.metadata)
        if record.labels:
            meta["labels"] = record.labels
        if record.notes:
            meta["notes"] = record.notes
        with logger.start_span(name=name) as span:
            span.log(
                input={"step_id": record.step_id, **record.inputs},
                output={"step_id": record.step_id, **record.outputs},
                metadata=meta or None,
            )
    except ConfigurationError:
        raise
    except Exception as exc:
        raise DependencyUnavailableError(f"Braintrust logging failed: {exc}") from exc


def run_step_eval(
    step_id: StepId,
    *,
    config: BraintrustConfig | None = None,
    **payload: Any,
) -> EvalRecord:
    """
    Build an :class:`~auto_prompt.evaluation.records.EvalRecord` and send it to Braintrust.

    Thin helper for callers that do not construct records by hand.

    :param step_id: Target step.
    :param config: Optional Braintrust config.
    :param payload: Must include keys required by the step-specific branch.
    :return: The record that was logged.
    """

    if step_id != "context_engineering":
        raise ConfigurationError(f"run_step_eval not implemented for step_id={step_id!r}")

    record = build_context_engineering_record(**payload)
    log_step(record, config=config)
    return record


def build_context_engineering_record(
    *,
    run_id: str | None = None,
    data_root: str,
    context_path: str,
    source_paths: list[str],
    merged_body: str,
    incremental_dedupe: bool,
) -> EvalRecord:
    """
    Construct a record for a completed context merge.

    :param run_id: Optional id; a random uuid is used if omitted.
    :param data_root: Root directory for scraped data.
    :param context_path: Absolute or project-relative path to ``prompt_methods_context.md``.
    :param source_paths: Relative paths of ``.md`` sources processed in this run.
    :param merged_body: Final merged Markdown written to disk.
    :param incremental_dedupe: Whether LM incremental dedupe was enabled.
    :return: Record ready for :func:`log_step`.
    """

    rid = run_id or str(uuid.uuid4())
    digest = hashlib.sha256(merged_body.encode("utf-8")).hexdigest()
    excerpt = merged_body[:2000] if len(merged_body) > 2000 else merged_body
    return EvalRecord(
        step_id="context_engineering",
        run_id=rid,
        inputs={
            "data_root": data_root,
            "source_md_paths": source_paths,
            "incremental_dedupe": incremental_dedupe,
        },
        outputs={
            "context_path": context_path,
            "merged_body_sha256": digest,
            "merged_body_chars": len(merged_body),
            "merged_body_excerpt": excerpt,
        },
        metadata={"sdk": "braintrust", "emitter": "auto_prompt.evaluation"},
    )
