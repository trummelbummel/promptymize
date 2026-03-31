from __future__ import annotations

from auto_prompt.promptymization.semantic_method_merge import (
    cluster_section_indices,
    jaccard_similarity,
    run_semantic_merge_pass,
)


def test_jaccard_similarity_overlapping_sections() -> None:
    a = "## Chain of thought prompting\n- ask the model to think step by step before answering."
    b = "## CoT style\n- use step by step reasoning for complex tasks."
    assert jaccard_similarity(a, b) > 0.05


def test_jaccard_similarity_unrelated_sections() -> None:
    a = "## Formatting\n- use bullet lists only."
    b = "## Temperature\n- lower values for deterministic outputs."
    assert jaccard_similarity(a, b) < 0.1


def test_cluster_section_indices_groups_similar() -> None:
    sections = [
        "## Structured output\n- specify json schema for responses.",
        "## JSON mode\n- require valid json output from the model.",
        "## Unrelated topic\n- use a low temperature setting for factual answers.",
    ]
    clusters = cluster_section_indices(sections, threshold=0.12)
    flat = sorted(i for g in clusters for i in g)
    assert flat == [0, 1, 2]
    # First two share json/schema vocabulary; third is distinct at this threshold.
    assert any(len(g) > 1 for g in clusters)


def test_run_semantic_merge_pass_calls_merger_for_multi_section_cluster() -> None:
    """When two sections are similar enough to cluster, merger runs once on the pair."""

    sections_md = (
        "## Method alpha\n"
        "- describe the task clearly before generation.\n\n"
        "## Method beta\n"
        "- clarify the objective before asking for output.\n"
    )
    calls: list[str] = []

    def merger(text: str) -> str:
        calls.append(text)
        return "## Combined\n- one consolidated rule.\n"

    out = run_semantic_merge_pass(
        sections_md,
        merger,
        similarity_threshold=0.08,
        max_chunk_chars=100_000,
    )
    assert "Combined" in out
    assert len(calls) >= 1
