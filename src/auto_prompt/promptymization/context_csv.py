from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

DEFAULT_CONTEXT_CSV = "prompt_methods_context.csv"


@dataclass(frozen=True)
class ContextMethodRow:
    """One prompt-method row from the canonical context CSV."""

    method_name: str
    model_type: str
    section_markdown: str


def default_context_csv_path() -> Path:
    """Return the default context CSV path under ``sources/data/context``."""

    project_root = Path(__file__).resolve().parents[3]
    return project_root / "sources" / "data" / "context" / DEFAULT_CONTEXT_CSV


def load_context_rows(
    *,
    context_path: Path | None = None,
    model_type: str | None = None,
    include_all_rows: bool = True,
) -> list[ContextMethodRow]:
    """
    Load context rows from CSV and optionally filter by ``model_type``.

    :param context_path: Optional explicit path to context CSV.
    :param model_type: Optional model-family label filter (e.g. ``gpt``, ``claude``).
    :param include_all_rows: Include rows labelled ``all`` when ``model_type`` is set.
    :return: Ordered rows from CSV after filtering.
    """

    path = context_path or default_context_csv_path()
    if not path.exists():
        return []

    wanted = (model_type or "").strip().lower()
    rows: list[ContextMethodRow] = []
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            method_name = str(row.get("method_name", "")).strip()
            row_model_type = str(row.get("model_type", "")).strip().lower()
            section_markdown = str(row.get("section_markdown", "")).strip()
            if not method_name or not row_model_type or not section_markdown:
                continue
            if wanted and row_model_type != wanted:
                if not (include_all_rows and row_model_type == "all"):
                    continue
            rows.append(
                ContextMethodRow(
                    method_name=method_name,
                    model_type=row_model_type,
                    section_markdown=section_markdown,
                )
            )
    return rows


def rows_to_markdown(rows: list[ContextMethodRow]) -> str:
    """
    Collapse filtered context rows into deduplicated markdown sections.

    Keeps first-seen order by ``section_markdown``.
    """

    seen: set[str] = set()
    out: list[str] = []
    for row in rows:
        section = row.section_markdown.strip()
        if not section or section in seen:
            continue
        seen.add(section)
        out.append(section)
    return "\n\n".join(out).strip()

