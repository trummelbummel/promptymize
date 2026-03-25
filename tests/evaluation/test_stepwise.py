"""Tests for stepwise evaluation (mocked Braintrust)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from auto_prompt.errors import ConfigurationError
from auto_prompt.evaluation import (
    build_context_engineering_record,
    build_end_to_end_stub,
    iter_observation_jsonl,
    log_step,
    trace_to_jsonable,
)
from auto_prompt.evaluation.config import BraintrustConfig, load_braintrust_config_from_env
from auto_prompt.evaluation.records import EvalRecord
from auto_prompt.evaluation.steps import STEP_ORDER


def test_load_braintrust_config_requires_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("BRAINTRUST_API_KEY", raising=False)
    with pytest.raises(ConfigurationError):
        load_braintrust_config_from_env()


def test_step_order_has_context_engineering_first() -> None:
    assert STEP_ORDER[0] == "context_engineering"


def test_build_context_engineering_record_hashes_body() -> None:
    record = build_context_engineering_record(
        data_root="/tmp/data",
        context_path="/tmp/data/context/prompt_methods_context.md",
        source_paths=["a/x.md"],
        merged_body="## Hello\n- rule",
        incremental_dedupe=False,
    )
    assert record.step_id == "context_engineering"
    assert record.inputs["source_md_paths"] == ["a/x.md"]
    assert len(record.outputs["merged_body_sha256"]) == 64
    assert "Hello" in record.outputs["merged_body_excerpt"]


def test_log_step_dispatches_to_braintrust(monkeypatch: pytest.MonkeyPatch) -> None:
    mock_logger = MagicMock()
    mock_span = MagicMock()
    mock_logger.start_span.return_value.__enter__ = MagicMock(return_value=mock_span)
    mock_logger.start_span.return_value.__exit__ = MagicMock(return_value=False)

    with patch("auto_prompt.evaluation.logging.init_logger", return_value=mock_logger):
        record = build_context_engineering_record(
            data_root="/data",
            context_path="/data/context/out.md",
            source_paths=[],
            merged_body="body",
            incremental_dedupe=False,
        )
        log_step(
            record,
            config=BraintrustConfig(api_key="k", project_id=None, project_name="p"),
        )

    mock_logger.start_span.assert_called_once()
    mock_span.log.assert_called_once()


def test_log_step_unknown_step() -> None:
    rec = EvalRecord(
        step_id="agent_turn",
        run_id="r",
        inputs={},
        outputs={},
    )
    with pytest.raises(ConfigurationError):
        log_step(rec, config=BraintrustConfig(api_key="k", project_id=None, project_name="p"))


def test_iter_observation_jsonl_roundtrip(tmp_path: Path) -> None:
    p = tmp_path / "obs.jsonl"
    p.write_text(
        '{"step_id":"context_engineering","run_id":"1","inputs":{},"outputs":{}}\n',
        encoding="utf-8",
    )
    rows = list(iter_observation_jsonl(p))
    assert len(rows) == 1
    assert rows[0].run_id == "1"


def test_end_to_end_stub() -> None:
    stub = build_end_to_end_stub(session_id="s")
    assert trace_to_jsonable(stub)["session_id"] == "s"
