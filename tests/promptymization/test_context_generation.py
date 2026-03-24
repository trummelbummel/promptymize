from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import dspy

from auto_prompt.promptymization.context_generation import PromptMethodsContext


def test_build_context_writes_merge_latest_and_aggregates(tmp_path: Path) -> None:
    data_root = tmp_path / "sources" / "data"
    (data_root / "batch1").mkdir(parents=True)
    (data_root / "batch1" / "a.md").write_text("# Src\nbody", encoding="utf-8")

    mock_summarizer = MagicMock()
    mock_summarizer.return_value = dspy.Prediction(summary="## One\n- rule")

    pipeline = PromptMethodsContext(summarizer=mock_summarizer, data_root=data_root)
    out = pipeline.build_context()

    assert out.name == "prompt_methods_context.md"
    assert out.parent == data_root / "context"
    assert "## One" in out.read_text(encoding="utf-8")
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

    text = out.read_text(encoding="utf-8")
    assert text.count("## Same") == 1
    assert text.count("- one") == 1


def test_build_context_merges_into_existing_latest(tmp_path: Path) -> None:
    data_root = tmp_path / "sources" / "data"
    ctx = data_root / "context"
    ctx.mkdir(parents=True)
    (ctx / "prompt_methods_context.md").write_text("## Existing\n- keep\n", encoding="utf-8")

    (data_root / "z").mkdir(parents=True)
    (data_root / "z" / "f.md").write_text("x", encoding="utf-8")

    mock_summarizer = MagicMock()
    mock_summarizer.return_value = dspy.Prediction(summary="## New\n- add\n")

    pipeline = PromptMethodsContext(summarizer=mock_summarizer, data_root=data_root)
    out = pipeline.build_context()

    assert out.name == "prompt_methods_context.md"
    out_text = out.read_text(encoding="utf-8")
    assert "## Existing" in out_text and "- keep" in out_text
    assert "## New" in out_text and "- add" in out_text
