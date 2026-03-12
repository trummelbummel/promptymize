from __future__ import annotations

from unittest.mock import patch

import dspy

from auto_prompt.promptymization.dspy_modules import (
    DeduplicatePromptSection,
    SummarizePromptMethods,
    TextSummarizer,
)


# -- SummarizePromptMethods signature --------------------------------------


def test_summarize_prompt_methods_has_expected_fields() -> None:
    fields = SummarizePromptMethods.model_fields
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


# -- DeduplicatePromptSection ----------------------------------------------


def test_deduplicate_returns_full_section_when_no_match() -> None:
    """Sections absent from the reference file are returned in full."""

    new_text = "## Chain of Thought\n- Step by step reasoning\n- Break down complex tasks"
    reference_file = "## Few-Shot Prompting\n- Provide examples\n- Use diverse examples"

    dedup = DeduplicatePromptSection()

    header_pred = dspy.Prediction(markdown_header="NONE", reasoning="")
    with patch.object(dedup, "find_header", return_value=header_pred):
        result = dedup.forward(new_text=new_text, reference_file=reference_file)

    assert len(result.sections) == 1
    assert "Chain of Thought" in result.sections[0]
    assert "Step by step reasoning" in result.novel_content


def test_deduplicate_returns_only_novel_bullets_when_match_found() -> None:
    """When a matching header exists, only novel bullets are kept."""

    new_text = "## Few-Shot Prompting\n- Provide examples\n- Use chain-of-thought in examples"
    reference_file = "## Few-Shot Prompting\n- Provide examples\n- Use diverse examples"

    dedup = DeduplicatePromptSection()

    header_pred = dspy.Prediction(markdown_header="## Few-Shot Prompting", reasoning="")
    novel_pred = dspy.Prediction(
        novel_bullets="## Few-Shot Prompting\n- Use chain-of-thought in examples",
        reasoning="",
    )

    with (
        patch.object(dedup, "find_header", return_value=header_pred),
        patch.object(dedup, "find_novel", return_value=novel_pred),
    ):
        result = dedup.forward(new_text=new_text, reference_file=reference_file)

    assert len(result.sections) == 1
    assert "chain-of-thought" in result.novel_content
    assert "Provide examples" not in result.novel_content


def test_deduplicate_drops_section_when_all_bullets_duplicate() -> None:
    """When every bullet is already covered, the section is dropped entirely."""

    new_text = "## Few-Shot Prompting\n- Provide examples"
    reference_file = "## Few-Shot Prompting\n- Provide examples\n- Use diverse examples"

    dedup = DeduplicatePromptSection()

    header_pred = dspy.Prediction(markdown_header="## Few-Shot Prompting", reasoning="")
    novel_pred = dspy.Prediction(novel_bullets="NONE", reasoning="")

    with (
        patch.object(dedup, "find_header", return_value=header_pred),
        patch.object(dedup, "find_novel", return_value=novel_pred),
    ):
        result = dedup.forward(new_text=new_text, reference_file=reference_file)

    assert result.sections == []
    assert result.novel_content == ""


def test_deduplicate_handles_multiple_sections() -> None:
    """Mixed scenario: one section matches, another is entirely new."""

    new_text = (
        "## Few-Shot Prompting\n- Provide examples\n"
        "## Chain of Thought\n- Step by step reasoning"
    )
    reference_file = "## Few-Shot Prompting\n- Provide examples\n- Use diverse examples"

    dedup = DeduplicatePromptSection()

    def fake_find_header(new_section: str, reference_file: str) -> dspy.Prediction:  # noqa: ARG001
        if "Few-Shot" in new_section:
            return dspy.Prediction(markdown_header="## Few-Shot Prompting", reasoning="")
        return dspy.Prediction(markdown_header="NONE", reasoning="")

    novel_pred = dspy.Prediction(novel_bullets="NONE", reasoning="")

    with (
        patch.object(dedup, "find_header", side_effect=fake_find_header),
        patch.object(dedup, "find_novel", return_value=novel_pred),
    ):
        result = dedup.forward(new_text=new_text, reference_file=reference_file)

    assert len(result.sections) == 1
    assert "Chain of Thought" in result.sections[0]


def test_deduplicate_is_dspy_module() -> None:
    assert isinstance(DeduplicatePromptSection(), dspy.Module)
