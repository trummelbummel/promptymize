from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

DEFAULT_CONTEXT_CSV = "prompt_methods_context.csv"
CSV_METHOD_NAME = "method_name"
CSV_MODEL_TYPE = "model_type"
CSV_SECTION_MARKDOWN = "section_markdown"
MODEL_TYPE_ALL = "all"


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
    loaded: list[ContextMethodRow] = []
    with path.open("r", encoding="utf-8", newline="") as f:
        for raw in csv.DictReader(f):
            parsed = _parse_row(raw)
            if parsed is None:
                continue
            if not _matches_model_type(
                row_model_type=parsed.model_type,
                wanted=wanted,
                include_all_rows=include_all_rows,
            ):
                continue
            loaded.append(parsed)
    return loaded


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


def _parse_row(raw: dict[str, str]) -> ContextMethodRow | None:
    method_name = str(raw.get(CSV_METHOD_NAME, "")).strip()
    row_model_type = str(raw.get(CSV_MODEL_TYPE, "")).strip().lower()
    section_markdown = str(raw.get(CSV_SECTION_MARKDOWN, "")).strip()
    if not method_name or not row_model_type or not section_markdown:
        return None
    return ContextMethodRow(
        method_name=method_name,
        model_type=row_model_type,
        section_markdown=section_markdown,
    )


def _matches_model_type(*, row_model_type: str, wanted: str, include_all_rows: bool) -> bool:
    if not wanted:
        return True
    if row_model_type == wanted:
        return True
    return include_all_rows and row_model_type == MODEL_TYPE_ALL

