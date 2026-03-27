from __future__ import annotations

from pathlib import Path

from auto_prompt.promptymization.context_csv import load_context_rows, rows_to_markdown


def test_load_context_rows_filters_model_and_keeps_all(tmp_path: Path) -> None:
    context_path = tmp_path / "prompt_methods_context.csv"
    context_path.write_text(
        "method_name,model_type,section_markdown\n"
        "\"Universal\",\"all\",\"## Universal\n- Works anywhere\"\n"
        "\"Claude Only\",\"claude\",\"## Claude Only\n- Use XML tags\"\n"
        "\"GPT Only\",\"gpt\",\"## GPT Only\n- Ask for JSON schema\"\n",
        encoding="utf-8",
    )

    rows = load_context_rows(context_path=context_path, model_type="claude")
    assert [r.method_name for r in rows] == ["Universal", "Claude Only"]


def test_rows_to_markdown_dedupes_duplicate_sections() -> None:
    class Row:
        def __init__(self, section_markdown: str) -> None:
            self.section_markdown = section_markdown

    rows = [
        Row("## Shared\n- One"),
        Row("## Shared\n- One"),
        Row("## Model\n- Two"),
    ]
    text = rows_to_markdown(rows)  # type: ignore[arg-type]
    assert text.count("## Shared") == 1
    assert "## Model" in text

