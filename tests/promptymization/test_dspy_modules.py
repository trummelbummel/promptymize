from __future__ import annotations

from unittest.mock import MagicMock, patch

import dspy

from auto_prompt.promptymization.dspy_modules import SummarizeText, TextSummarizer


# -- SummarizeText signature -----------------------------------------------


def test_summarize_text_has_expected_fields() -> None:
    fields = SummarizeText.model_fields
    assert "text" in fields
    assert "summary" in fields


# -- TextSummarizer --------------------------------------------------------


def test_text_summarizer_forward_splits_on_headers() -> None:
    summary_md = "## Overview\nBullet 1\n## Details\nBullet 2"
    mock_prediction = dspy.Prediction(summary=summary_md)

    summarizer = TextSummarizer()
    with patch.object(summarizer, "summarize", return_value=mock_prediction) as mock_cot:
        result = summarizer.forward(text="Some long text")

    mock_cot.assert_called_once_with(text="Some long text")
    assert result.summary == summary_md
    assert len(result.sections) == 2
    assert result.sections[0].startswith("## Overview")
    assert result.sections[1].startswith("## Details")


def test_text_summarizer_forward_no_headers_returns_single_section() -> None:
    summary_md = "Just a plain summary without any headers."
    mock_prediction = dspy.Prediction(summary=summary_md)

    summarizer = TextSummarizer()
    with patch.object(summarizer, "summarize", return_value=mock_prediction):
        result = summarizer.forward(text="Input")

    assert len(result.sections) == 1
    assert "plain summary" in result.sections[0]


def test_text_summarizer_forward_empty_summary() -> None:
    mock_prediction = dspy.Prediction(summary="")

    summarizer = TextSummarizer()
    with patch.object(summarizer, "summarize", return_value=mock_prediction):
        result = summarizer.forward(text="Input")

    assert result.sections == []


def test_text_summarizer_is_dspy_module() -> None:
    summarizer = TextSummarizer()
    assert isinstance(summarizer, dspy.Module)
