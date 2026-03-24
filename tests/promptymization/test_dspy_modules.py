from __future__ import annotations

from unittest.mock import patch

import dspy

from auto_prompt.promptymization.dspy_modules import (
    DeduplicatePromptSection,
    PromptMethodSummarizer,
    SummarizePromptMethods,
)


# -- SummarizePromptMethods signature --------------------------------------


def test_summarize_prompt_methods_has_expected_fields() -> None:
    fields = SummarizePromptMethods.model_fields
    assert "text" in fields
    assert "summary" in fields


# -- PromptMethodSummarizer ------------------------------------------------


def test_prompt_method_summarizer_forward_splits_on_headers() -> None:
    summary_md = "## Overview\nBullet 1\n## Details\nBullet 2"
    mock_prediction = dspy.Prediction(summary=summary_md)

    summarizer = PromptMethodSummarizer()
    with patch.object(summarizer, "summarize", return_value=mock_prediction) as mock_cot:
        result = summarizer.forward(text="Some long text")

    mock_cot.assert_called_once_with(text="Some long text")
    assert result.summary == summary_md
    assert result.headers == ["## Overview", "## Details"]
    assert result.sections == [
        "## Overview\nBullet 1",
        "## Details\nBullet 2",
    ]


def test_prompt_method_summarizer_forward_no_headers_returns_single_section() -> None:
    summary_md = "Just a plain summary without any headers."
    mock_prediction = dspy.Prediction(summary=summary_md)

    summarizer = PromptMethodSummarizer()
    with patch.object(summarizer, "summarize", return_value=mock_prediction):
        result = summarizer.forward(text="Input")

    assert result.headers == []
    assert result.sections == ["Just a plain summary without any headers."]


def test_prompt_method_summarizer_forward_empty_summary() -> None:
    mock_prediction = dspy.Prediction(summary="")

    summarizer = PromptMethodSummarizer()
    with patch.object(summarizer, "summarize", return_value=mock_prediction):
        result = summarizer.forward(text="Input")

    assert result.sections == []


def test_prompt_method_summarizer_is_dspy_module() -> None:
    summarizer = PromptMethodSummarizer()
    assert isinstance(summarizer, dspy.Module)


# -- DeduplicatePromptSection ----------------------------------------------

