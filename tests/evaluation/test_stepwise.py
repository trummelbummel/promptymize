"""Tests for stepwise evaluation (mocked Braintrust)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from auto_prompt.errors import ConfigurationError
from auto_prompt.evaluation import (
    build_agent_turn_record,
    build_context_engineering_record,
    build_end_to_end_record,
    build_end_to_end_stub,
    build_scraper_markdown_record,
    iter_observation_jsonl,
    log_step,
    run_step_eval,
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
        context_path="/tmp/data/context/prompt_methods_context.csv",
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
            context_path="/data/context/prompt_methods_context.csv",
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


def test_run_step_eval_context_engineering_dispatches() -> None:
    with patch("auto_prompt.evaluation.logging.log_step") as mock_log_step:
        rec = run_step_eval(
            "context_engineering",
            data_root="/tmp/data",
            context_path="/tmp/data/context/prompt_methods_context.csv",
            source_paths=["a.md"],
            merged_body="## A\n- b",
            incremental_dedupe=False,
        )
    assert rec.step_id == "context_engineering"
    mock_log_step.assert_called_once()


def test_run_step_eval_scraper_markdown_dispatches() -> None:
    with patch("auto_prompt.evaluation.logging.log_step") as mock_log_step:
        rec = run_step_eval(
            "scraper_markdown",
            source_url="https://example.com",
            output_path="sources/data/x/page.md",
            markdown_body="# title",
            folder_name="x",
        )
    assert rec.step_id == "scraper_markdown"
    mock_log_step.assert_called_once()


def test_run_step_eval_agent_turn_dispatches() -> None:
    with patch("auto_prompt.evaluation.logging.log_step") as mock_log_step:
        rec = run_step_eval(
            "agent_turn",
            prompt="Write a summary",
            scoring_phase="before",
            scorer_name="keyword_alignment",
            score=0.5,
            explanation="some overlap",
        )
    assert rec.step_id == "agent_turn"
    mock_log_step.assert_called_once()


def test_run_step_eval_end_to_end_dispatches() -> None:
    with patch("auto_prompt.evaluation.logging.log_step") as mock_log_step:
        rec = run_step_eval(
            "end_to_end",
            session_id="s-1",
            trace={"session_id": "s-1", "agent_turns": 2},
        )
    assert rec.step_id == "end_to_end"
    mock_log_step.assert_called_once()


def test_log_step_unknown_step() -> None:
    rec = EvalRecord(
        step_id="unknown_step",  # type: ignore[arg-type]
        run_id="r",
        inputs={},
        outputs={},
    )
    with pytest.raises(ConfigurationError):
        log_step(rec, config=BraintrustConfig(api_key="k", project_id=None, project_name="p"))


def test_build_agent_turn_record() -> None:
    rec = build_agent_turn_record(
        prompt="Write a concise summary",
        scoring_phase="before",
        scorer_name="keyword_alignment",
        score=0.7,
        explanation="Good keyword overlap",
        context_path="/tmp/data/context/prompt_methods_context.csv",
        dataset_size=0,
    )
    assert rec.step_id == "agent_turn"
    assert rec.outputs["score"] == 0.7
    assert rec.inputs["scoring_phase"] == "before"


def test_build_scraper_markdown_record() -> None:
    rec = build_scraper_markdown_record(
        source_url="https://example.com/docs",
        output_path="sources/data/x/page.md",
        markdown_body="# Title\nhello",
        folder_name="x",
    )
    assert rec.step_id == "scraper_markdown"
    assert rec.outputs["markdown_chars"] > 0
    assert len(rec.outputs["markdown_sha256"]) == 64


def test_build_end_to_end_record() -> None:
    rec = build_end_to_end_record(
        session_id="s-1",
        trace={"session_id": "s-1", "agent_turns": 3},
    )
    assert rec.step_id == "end_to_end"
    assert rec.inputs["session_id"] == "s-1"
    assert len(rec.outputs["trace_sha256"]) == 64


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
