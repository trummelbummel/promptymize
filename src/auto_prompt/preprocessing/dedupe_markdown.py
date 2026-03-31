from __future__ import annotations

import re
from dataclasses import dataclass, field

from auto_prompt.preprocessing.preprocessing import HtmlPreprocessor

_ATX_HEADER = re.compile(r"^#{1,6}\s+\S")


def exact_dedupe_prompt_method_markdown(markdown: str) -> str:
    """
    Merge sections that share the same first-line header and dedupe bullet lines.

    Operates on Markdown produced by summarizers: splits on ATX headers, then
    for each header keeps the first occurrence order and unique lines
    (exact string match) in first-seen order.
    """

    stripped = markdown.strip()
    if not stripped:
        return ""

    sections = HtmlPreprocessor.split_on_headers(stripped)
    if not sections:
        return stripped + "\n"

    by_header: dict[str, _SectionMerge] = {}
    header_order: list[str] = []
    preambles: list[str] = []
    seen_preamble: set[str] = set()

    for raw in sections:
        block = _normalize_block(raw)
        if block == "":
            continue
        lines = block.splitlines()
        first = _header_line(lines)
        if first and _ATX_HEADER.match(first):
            if first not in by_header:
                header_order.append(first)
                by_header[first] = _SectionMerge()
            by_header[first].add_lines(lines[1:])
            continue
        if block not in seen_preamble:
            seen_preamble.add(block)
            preambles.append(block)

    out = _render_deduped_markdown(
        preambles=preambles,
        header_order=header_order,
        by_header=by_header,
    )
    return out


def _normalize_block(raw: str) -> str:
    return raw.strip()


def _header_line(lines: list[str]) -> str:
    return lines[0].strip() if lines else ""


def _render_deduped_markdown(
    *,
    preambles: list[str],
    header_order: list[str],
    by_header: dict[str, "_SectionMerge"],
) -> str:
    parts: list[str] = []
    for pre in preambles:
        parts.append(pre)
        parts.append("")

    for h in header_order:
        merge = by_header[h]
        parts.append(h)
        parts.extend(merge.lines_out())
        parts.append("")

    out = "\n".join(parts).strip()
    return out + "\n" if out else ""


@dataclass(slots=True)
class _SectionMerge:
    """Collect unique lines under one header."""

    _seen: set[str] = field(default_factory=set)
    _ordered: list[str] = field(default_factory=list)

    def add_lines(self, body_lines: list[str]) -> None:
        for line in body_lines:
            if not line.strip():
                continue
            if line in self._seen:
                continue
            self._seen.add(line)
            self._ordered.append(line)

    def lines_out(self) -> list[str]:
        return list(self._ordered)

__all__ = ["exact_dedupe_prompt_method_markdown"]

