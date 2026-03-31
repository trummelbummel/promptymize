"""Log pipeline steps to Braintrust via the official SDK."""

from __future__ import annotations

import hashlib
import uuid
from typing import Any

from braintrust import init_logger

from auto_prompt.errors import ConfigurationError, DependencyUnavailableError
from auto_prompt.evaluation.config import BraintrustConfig, load_braintrust_config_from_env
from auto_prompt.evaluation.records import EvalRecord
from auto_prompt.evaluation.steps import STEP_ORDER, StepId

_EMITTER_META = {"sdk": "braintrust", "emitter": "auto_prompt.evaluation"}


def _run_id(run_id: str | None) -> str:
    """Return ``run_id`` or a new UUID4 string when omitted."""

    return run_id or str(uuid.uuid4())


def _sha256_hex(text: str) -> str:
    """Hex-encoded SHA-256 of ``text`` (UTF-8)."""

    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _text_excerpt(text: str, *, max_len: int = 2000) -> str:
    """Return ``text`` unchanged if short, else a prefix of length ``max_len``."""

    if len(text) <= max_len:
        return text
    return text[:max_len]


def _merge_emitter_metadata(extra: dict[str, Any] | None) -> dict[str, Any]:
    """Emitter fields for Braintrust rows, merged with optional ``extra``."""

    if not extra:
        return dict(_EMITTER_META)
    return {**_EMITTER_META, **extra}


def _span_metadata(record: EvalRecord) -> dict[str, Any]:
    """Span ``metadata`` payload: record metadata plus optional labels and notes."""

    meta: dict[str, Any] = dict(record.metadata)
    if record.labels:
        meta["labels"] = record.labels
    if record.notes:
        meta["notes"] = record.notes
    return meta


def log_step(
    record: EvalRecord,
    *,
    config: BraintrustConfig | None = None,
) -> None:
    """
    Dispatch a single :class:`~auto_prompt.evaluation.records.EvalRecord` to Braintrust.

    Supports ``context_engineering``, ``scraper_markdown``, ``agent_turn``, and ``end_to_end``.
    Other step ids raise ``ConfigurationError``.

    :param record: Row to log.
    :param config: Optional config; defaults to env via :func:`load_braintrust_config_from_env`.
    :return: None.
    :raises ConfigurationError: Unknown step or missing config when needed.
    :raises DependencyUnavailableError: Braintrust client or network failure.
    """

    cfg = config if config is not None else load_braintrust_config_from_env()
    if record.step_id not in STEP_ORDER:
        raise ConfigurationError(f"Unsupported step_id for logging: {record.step_id!r}")
    _log_record(record, cfg)


def _log_record(record: EvalRecord, config: BraintrustConfig) -> None:
    """Emit a step record span under a Braintrust project logger."""

    try:
        logger = init_logger(
            project=config.project_name,
            project_id=config.project_id,
            api_key=config.api_key,
            set_current=False,
        )
        name = f"{record.step_id}:{record.run_id}"
        meta = _span_metadata(record)
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

    if step_id == "context_engineering":
        record = build_context_engineering_record(**payload)
    elif step_id == "scraper_markdown":
        record = build_scraper_markdown_record(**payload)
    elif step_id == "agent_turn":
        record = build_agent_turn_record(**payload)
    elif step_id == "end_to_end":
        record = build_end_to_end_record(**payload)
    else:
        raise ConfigurationError(f"run_step_eval not implemented for step_id={step_id!r}")
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
    :param context_path: Absolute or project-relative path to ``prompt_methods_context.csv``.
    :param source_paths: Relative paths of ``.md`` sources processed in this run.
    :param merged_body: Final merged Markdown written to disk.
    :param incremental_dedupe: Whether LM incremental dedupe was enabled.
    :return: Record ready for :func:`log_step`.
    """

    rid = _run_id(run_id)
    digest = _sha256_hex(merged_body)
    excerpt = _text_excerpt(merged_body)
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
        metadata=_merge_emitter_metadata(),
    )


def build_agent_turn_record(
    *,
    prompt: str,
    scoring_phase: str,
    scorer_name: str,
    score: float,
    explanation: str,
    context_path: str | None = None,
    dataset_size: int = 0,
    method_id: str | None = None,
    session_id: str | None = None,
    metadata: dict[str, Any] | None = None,
    run_id: str | None = None,
) -> EvalRecord:
    """Construct a record for one prompt-scorer invocation."""

    rid = _run_id(run_id)
    prompt_digest = _sha256_hex(prompt)
    return EvalRecord(
        step_id="agent_turn",
        run_id=rid,
        inputs={
            "prompt_sha256": prompt_digest,
            "prompt_chars": len(prompt),
            "scoring_phase": scoring_phase,
            "scorer_name": scorer_name,
            "context_path": context_path,
            "dataset_size": dataset_size,
            "method_id": method_id,
            "session_id": session_id,
        },
        outputs={
            "score": float(score),
            "explanation": explanation,
        },
        metadata=_merge_emitter_metadata(metadata),
    )


def build_scraper_markdown_record(
    *,
    source_url: str,
    output_path: str,
    markdown_body: str,
    folder_name: str | None = None,
    run_id: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> EvalRecord:
    """Construct a record for one scraper markdown output."""

    rid = _run_id(run_id)
    digest = _sha256_hex(markdown_body)
    excerpt = _text_excerpt(markdown_body)
    return EvalRecord(
        step_id="scraper_markdown",
        run_id=rid,
        inputs={
            "source_url": source_url,
            "folder_name": folder_name,
        },
        outputs={
            "output_path": output_path,
            "markdown_sha256": digest,
            "markdown_chars": len(markdown_body),
            "markdown_excerpt": excerpt,
        },
        metadata=_merge_emitter_metadata(metadata),
    )


def build_end_to_end_record(
    *,
    session_id: str,
    trace: dict[str, Any],
    run_id: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> EvalRecord:
    """Construct a record for one end-to-end user session trace."""

    rid = _run_id(run_id)
    trace_json = str(trace)
    digest = _sha256_hex(trace_json)
    return EvalRecord(
        step_id="end_to_end",
        run_id=rid,
        inputs={
            "session_id": session_id,
        },
        outputs={
            "trace": trace,
            "trace_sha256": digest,
        },
        metadata=_merge_emitter_metadata(metadata),
    )
