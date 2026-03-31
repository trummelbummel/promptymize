from __future__ import annotations

from auto_prompt.preprocessing.dedupe_markdown import exact_dedupe_prompt_method_markdown


def test_exact_dedupe_merges_duplicate_headers_and_bullets() -> None:
    md = "## Method\n- a\n- b\n\n## Method\n- a\n- c\n"
    out = exact_dedupe_prompt_method_markdown(md)
    assert out.count("## Method") == 1
    assert "- a" in out
    assert "- b" in out
    assert "- c" in out


def test_exact_dedupe_empty() -> None:
    assert exact_dedupe_prompt_method_markdown("") == ""
    assert exact_dedupe_prompt_method_markdown("   \n") == ""

