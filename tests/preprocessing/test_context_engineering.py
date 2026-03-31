from __future__ import annotations

import csv
from pathlib import Path
from unittest.mock import MagicMock

import dspy

from auto_prompt.errors import ConcurrencyError
from auto_prompt.preprocessing.context_engineering import (
    CONTEXT_LOCK_FILENAME,
    PromptMethodsContext,
)


def _read_context_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def test_build_context_writes_merge_latest_and_aggregates(tmp_path: Path) -> None:
    data_root = tmp_path / "sources" / "data"
    (data_root / "batch1").mkdir(parents=True)
    (data_root / "batch1" / "a.md").write_text("# Src\nbody", encoding="utf-8")

    mock_summarizer = MagicMock()
    mock_summarizer.return_value = dspy.Prediction(summary="## One\n- rule")

    pipeline = PromptMethodsContext(summarizer=mock_summarizer, data_root=data_root)
    out = pipeline.build_context()

    assert out.name == "prompt_methods_context.csv"
    assert out.parent == data_root / "context"
    rows = _read_context_rows(out)
    assert len(rows) == 1
    assert rows[0]["method_name"] == "One"
    assert rows[0]["model_type"] == "all"
    assert "## One" in rows[0]["section_markdown"]
    mock_summarizer.assert_called_once_with(text="# Src\nbody")


def test_build_context_skips_processed_and_context_dirs(tmp_path: Path) -> None:
    data_root = tmp_path / "sources" / "data"
    (data_root / "processed" / "x").mkdir(parents=True)
    (data_root / "processed" / "x" / "skip.md").write_text("no", encoding="utf-8")
    (data_root / "context").mkdir(parents=True)
    (data_root / "context" / "skip2.md").write_text("no", encoding="utf-8")
    (data_root / "ok").mkdir(parents=True)
    (data_root / "ok" / "yes.md").write_text("yes", encoding="utf-8")

    mock_summarizer = MagicMock()
    mock_summarizer.return_value = dspy.Prediction(summary="S")

    pipeline = PromptMethodsContext(summarizer=mock_summarizer, data_root=data_root)
    pipeline.build_context()

    assert mock_summarizer.call_count == 1
    mock_summarizer.assert_called_once_with(text="yes")


def test_build_context_exact_dedupe_collapses_duplicate_sections(tmp_path: Path) -> None:
    data_root = tmp_path / "sources" / "data"
    (data_root / "d1").mkdir(parents=True)
    (data_root / "d1" / "a.md").write_text("src1", encoding="utf-8")
    (data_root / "d2").mkdir(parents=True)
    (data_root / "d2" / "b.md").write_text("src2", encoding="utf-8")

    mock_summarizer = MagicMock()
    mock_summarizer.return_value = dspy.Prediction(summary="## Same\n- one\n")

    pipeline = PromptMethodsContext(summarizer=mock_summarizer, data_root=data_root)
    out = pipeline.build_context()

    rows = _read_context_rows(out)
    assert len(rows) == 1
    assert rows[0]["method_name"] == "Same"
    assert rows[0]["section_markdown"].count("- one") == 1


def test_build_context_merges_into_existing_latest(tmp_path: Path) -> None:
    data_root = tmp_path / "sources" / "data"
    ctx = data_root / "context"
    ctx.mkdir(parents=True)
    (ctx / "prompt_methods_context.csv").write_text(
        "method_name,model_type,section_markdown\n"
        "\"Existing\",\"all\",\"## Existing\n- keep\"\n",
        encoding="utf-8",
    )

    (data_root / "z").mkdir(parents=True)
    (data_root / "z" / "f.md").write_text("x", encoding="utf-8")

    mock_summarizer = MagicMock()
    mock_summarizer.return_value = dspy.Prediction(summary="## New\n- add\n")

    pipeline = PromptMethodsContext(summarizer=mock_summarizer, data_root=data_root)
    out = pipeline.build_context()

    assert out.name == "prompt_methods_context.csv"
    rows = _read_context_rows(out)
    sections = [r["section_markdown"] for r in rows]
    assert any("## Existing" in s and "- keep" in s for s in sections)
    assert any("## New" in s and "- add" in s for s in sections)


def test_build_context_chunks_long_inputs(tmp_path: Path) -> None:
    data_root = tmp_path / "sources" / "data"
    (data_root / "batch1").mkdir(parents=True)

    # No headers, so chunking falls back to character slicing.
    long_text = "x" * 25
    (data_root / "batch1" / "a.md").write_text(long_text, encoding="utf-8")

    mock_summarizer = MagicMock()
    mock_summarizer.side_effect = [
        dspy.Prediction(summary="## M0\n- zero\n"),
        dspy.Prediction(summary="## M1\n- one\n"),
        dspy.Prediction(summary="## M2\n- two\n"),
    ]

    pipeline = PromptMethodsContext(summarizer=mock_summarizer, data_root=data_root)
    out = pipeline.build_context(max_chunk_chars=10, chunk_long_sources=True)

    assert out.exists()
    rows = _read_context_rows(out)
    sections = [r["section_markdown"] for r in rows]
    assert sum("## M0" in s for s in sections) == 1
    assert sum("## M1" in s for s in sections) == 1
    assert sum("## M2" in s for s in sections) == 1

    assert mock_summarizer.call_count == 3
    chunk_lens = [len(call.kwargs["text"]) for call in mock_summarizer.call_args_list]
    assert chunk_lens == [10, 10, 5]


def test_build_context_lock_timeout_raises(tmp_path: Path) -> None:
    data_root = tmp_path / "sources" / "data"
    (data_root / "context").mkdir(parents=True)
    (data_root / "batch1").mkdir(parents=True)
    (data_root / "batch1" / "a.md").write_text("x", encoding="utf-8")

    mock_summarizer = MagicMock()
    pipeline = PromptMethodsContext(summarizer=mock_summarizer, data_root=data_root)

    lock_path = pipeline.context_root / CONTEXT_LOCK_FILENAME
    lock_path.write_text("held", encoding="utf-8")
    try:
        raised = False
        try:
            pipeline.build_context(lock_timeout_seconds=0.0)
        except ConcurrencyError:
            raised = True
        assert raised
    finally:
        if lock_path.exists():
            lock_path.unlink()


def test_build_context_explodes_rows_for_multiple_model_labels(tmp_path: Path) -> None:
    data_root = tmp_path / "sources" / "data"
    (data_root / "batch1").mkdir(parents=True)
    (data_root / "batch1" / "a.md").write_text("src", encoding="utf-8")

    mock_summarizer = MagicMock()
    mock_summarizer.return_value = dspy.Prediction(
        summary="## Structured prompting\n- Works well for GPT and Claude families.\n",
    )

    out = PromptMethodsContext(summarizer=mock_summarizer, data_root=data_root).build_context()
    rows = _read_context_rows(out)
    model_types = sorted(r["model_type"] for r in rows)
    assert model_types == ["claude", "gpt"]
    assert len({r["section_markdown"] for r in rows}) == 1


def test_build_context_falls_back_to_processed_when_no_fresh_sources(tmp_path: Path) -> None:
    data_root = tmp_path / "sources" / "data"
    processed_batch = data_root / "processed" / "batch1"
    processed_batch.mkdir(parents=True)
    (processed_batch / "a.md").write_text("source text", encoding="utf-8")

    mock_summarizer = MagicMock()
    mock_summarizer.return_value = dspy.Prediction(summary="## Fallback\n- from processed")

    out = PromptMethodsContext(summarizer=mock_summarizer, data_root=data_root).build_context()
    rows = _read_context_rows(out)
    assert rows
    assert rows[0]["method_name"] == "Fallback"

