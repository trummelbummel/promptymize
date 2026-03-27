from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from auto_prompt.errors import ResourceNotFoundError, ValidationError
from auto_prompt.prompt_scorer import PromptScorer


def _write_context_csv(path: Path) -> None:
    path.write_text(
        "method_name,model_type,section_markdown\n"
        "\"Universal\",\"all\",\"## Universal\n- State output format clearly\"\n"
        "\"Claude XML\",\"claude\",\"## Claude XML\n- Use XML tags\"\n"
        "\"GPT JSON\",\"gpt\",\"## GPT JSON\n- Ask for JSON schema\"\n",
        encoding="utf-8",
    )


def test_score_context_only_filters_by_model_type(tmp_path: Path) -> None:
    context_path = tmp_path / "prompt_methods_context.csv"
    _write_context_csv(context_path)
    scorer = PromptScorer()

    result = scorer.score(
        "Use JSON schema and output format instructions",
        scoring_phase="before",
        scorer_name="keyword_alignment",
        model_type="gpt",
        context_path=context_path,
    )
    assert 0.0 <= result.score <= 1.0
    assert result.scoring_phase == "before"
    assert result.metadata["model_type"] == "gpt"


def test_score_method_id_not_found_raises(tmp_path: Path) -> None:
    context_path = tmp_path / "prompt_methods_context.csv"
    _write_context_csv(context_path)
    scorer = PromptScorer()

    with pytest.raises(ResourceNotFoundError):
        scorer.score(
            "hello",
            scoring_phase="before",
            scorer_name="keyword_alignment",
            context_path=context_path,
            method_id="does-not-exist",
        )


def test_score_unknown_profile_raises(tmp_path: Path) -> None:
    context_path = tmp_path / "prompt_methods_context.csv"
    _write_context_csv(context_path)
    scorer = PromptScorer()

    with pytest.raises(ValidationError):
        scorer.score(
            "hello",
            scoring_phase="before",
            scorer_name="unknown_profile",
            context_path=context_path,
        )


def test_compare_returns_before_after_and_delta(tmp_path: Path) -> None:
    context_path = tmp_path / "prompt_methods_context.csv"
    _write_context_csv(context_path)
    scorer = PromptScorer()

    result = scorer.compare(
        "Write answer",
        "Write answer using JSON schema and explicit output format",
        scorer_name="keyword_alignment",
        context_path=context_path,
        model_type="gpt",
    )
    assert result.before.scoring_phase == "before"
    assert result.after.scoring_phase == "after"
    assert abs(result.delta - (result.after.score - result.before.score)) < 1e-9


def test_score_emits_stepwise_when_enabled(tmp_path: Path) -> None:
    context_path = tmp_path / "prompt_methods_context.csv"
    _write_context_csv(context_path)
    scorer = PromptScorer()

    with patch("auto_prompt.prompt_scorer.run_step_eval") as mock_eval:
        scorer.score(
            "Use XML tags",
            scoring_phase="after",
            scorer_name="keyword_alignment",
            model_type="claude",
            context_path=context_path,
            emit_stepwise_eval=True,
        )
    mock_eval.assert_called_once()

