from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from auto_prompt.prompt_optimizer.agent import PromptOptimizerAgent, format_costar_markdown


def test_format_costar_markdown_uses_headers() -> None:
    text = format_costar_markdown(
        objectives="Ship faster",
        fields={
            "context": "SaaS",
            "objective": "Summarize",
            "style": "bullets",
            "tone": "neutral",
            "audience": "PMs",
            "response": "md",
        },
    )
    assert "## Task objectives" in text
    assert "Ship faster" in text
    assert "## Context" in text and "SaaS" in text
    assert "## Response" in text and "md" in text


def test_agent_loads_csv_context_filtered_by_model_type(tmp_path: Path) -> None:
    context_path = tmp_path / "prompt_methods_context.csv"
    context_path.write_text(
        "method_name,model_type,section_markdown\n"
        "\"Universal\",\"all\",\"## Universal\n- Works anywhere\"\n"
        "\"Claude Only\",\"claude\",\"## Claude Only\n- Use XML tags\"\n"
        "\"GPT Only\",\"gpt\",\"## GPT Only\n- Ask for JSON schema\"\n",
        encoding="utf-8",
    )
    agent = PromptOptimizerAgent(model_type="claude", context_path=context_path)

    md = agent.load_context_markdown()
    assert "## Universal" in md
    assert "## Claude Only" in md
    assert "## GPT Only" not in md


def test_agent_uses_single_call_for_costar_extension() -> None:
    agent = PromptOptimizerAgent(model_type="gpt")
    generator = MagicMock(
        return_value={
            "context": "enterprise helpdesk",
            "objective": "summarize tickets",
            "style": "bulleted",
            "tone": "professional",
            "audience": "support leads",
            "response": "markdown",
        }
    )
    draft = agent.generate_costar_extension(
        objectives="improve turnaround time",
        current_answers={"objective": "summarize tickets"},
        extension_generator=generator,
    )

    generator.assert_called_once()
    assert draft.fields["objective"] == "summarize tickets"
    assert draft.fields["audience"] == "support leads"


def test_agent_requires_user_approval_before_apply() -> None:
    agent = PromptOptimizerAgent(model_type="gpt")
    draft = agent.generate_costar_extension(
        objectives="reduce ambiguity",
        current_answers={"context": "internal policy QA"},
        extension_generator=lambda _: {
            "context": "internal policy QA",
            "objective": "answer policy questions",
            "style": "concise",
            "tone": "neutral",
            "audience": "employees",
            "response": "short bullet list",
        },
    )
    assert draft.fields["tone"] == "neutral"

    with pytest.raises(ValueError):
        agent.apply_verified_extension(user_prompt="Please help with policy")

    approved = agent.approve_costar_extension(edited_fields={"tone": "friendly"})
    assert approved.fields["tone"] == "friendly"
    updated = agent.apply_verified_extension(user_prompt="Please help with policy")
    assert "## Tone" in updated
    assert "friendly" in updated
    assert "- tone:" not in updated
    assert "## Task objectives" in updated


def test_agent_delegates_scoring_to_adapter() -> None:
    scorer = MagicMock()
    scorer.score.return_value = {"score": 0.91}
    agent = PromptOptimizerAgent(model_type="claude", scorer=scorer)

    result = agent.score_prompt(prompt="Write a summary", scoring_phase="before", session_id="s1")
    assert result == {"score": 0.91}
    scorer.score.assert_called_once_with(
        prompt="Write a summary",
        scoring_phase="before",
        model_type="claude",
        session_id="s1",
    )

