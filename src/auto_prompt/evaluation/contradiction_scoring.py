"""Heuristic scoring for contradictory prompt instructions."""

from __future__ import annotations

import re
from typing import Any, NamedTuple

_SPLIT_RE = re.compile(r"[\n\r]+|[.;]+")
_SCORE_STEP = 0.2


class _Rule(NamedTuple):
    """One dimension of possible conflict (e.g. verbosity vs brevity)."""

    dimension: str
    positive_label: str
    negative_label: str
    positive: re.Pattern[str]
    negative: re.Pattern[str]


_RULES: tuple[_Rule, ...] = (
    _Rule(
        "verbosity",
        "concise/brief",
        "detailed/comprehensive",
        re.compile(r"\b(concise|brief|short|succinct)\b", re.I),
        re.compile(r"\b(detailed|comprehensive|in[\s-]?depth|thorough)\b", re.I),
    ),
    _Rule(
        "length",
        "long output",
        "very short output",
        re.compile(r"\b(long|extensive|at least \d+ (?:words|paragraphs|pages))\b", re.I),
        re.compile(r"\b(one sentence|single sentence|under \d+ words|very short)\b", re.I),
    ),
    _Rule(
        "format",
        "use bullet points",
        "avoid bullet points",
        re.compile(r"\b(use|include|write in)\b.*\b(bullets?|bullet points?)\b", re.I),
        re.compile(r"\b(no|avoid|without)\b.*\b(bullets?|bullet points?)\b", re.I),
    ),
    _Rule(
        "code",
        "include code",
        "no code",
        re.compile(r"\b(include|show|provide)\b.*\b(code|snippet)\b", re.I),
        re.compile(r"\b(no|avoid|without|do not)\b.*\b(code|snippet)\b", re.I),
    ),
    _Rule(
        "certainty",
        "be certain",
        "state uncertainty",
        re.compile(r"\b(definitive|certain|confident|always)\b", re.I),
        re.compile(r"\b(uncertain|maybe|might|unknown|depends)\b", re.I),
    ),
)


def _split_instruction_clauses(prompt: str) -> list[str]:
    """
    Split ``prompt`` into coarse clauses on newlines and sentence boundaries.

    Collapses internal whitespace so regex matching runs on single-line strings.
    """

    clauses: list[str] = []
    for chunk in _SPLIT_RE.split(prompt):
        cleaned = " ".join(chunk.strip().split())
        if cleaned:
            clauses.append(cleaned)
    return clauses


def _hits_for_rule(clauses: list[str], rule: _Rule) -> tuple[list[str], list[str]]:
    """Return clauses matching the positive and negative patterns for ``rule``."""

    positive_hits = [c for c in clauses if rule.positive.search(c)]
    negative_hits = [c for c in clauses if rule.negative.search(c)]
    return positive_hits, negative_hits


def _contradiction_entry(
    rule: _Rule,
    positive_hits: list[str],
    negative_hits: list[str],
) -> dict[str, Any]:
    """Build one metadata entry describing a detected contradiction."""

    return {
        "dimension": rule.dimension,
        "positive_instruction": rule.positive_label,
        "negative_instruction": rule.negative_label,
        "examples": {
            "positive": positive_hits[:2],
            "negative": negative_hits[:2],
        },
    }


def _collect_contradictions(clauses: list[str]) -> list[dict[str, Any]]:
    """Apply all rules and return contradiction records (empty if none)."""

    out: list[dict[str, Any]] = []
    for rule in _RULES:
        pos, neg = _hits_for_rule(clauses, rule)
        if pos and neg:
            out.append(_contradiction_entry(rule, pos, neg))
    return out


def _build_explanation(contradictions: list[dict[str, Any]]) -> str:
    """Human-readable explanation matching prior scoring copy."""

    if not contradictions:
        return "No contradictory instructions were detected."

    parts = [
        f"{c['dimension']}: '{c['positive_instruction']}' conflicts with "
        f"'{c['negative_instruction']}'"
        for c in contradictions
    ]
    n = len(contradictions)
    return (
        f"Detected {n} contradictory instruction pair(s): " + "; ".join(parts) + "."
    )


def score_instruction_contradictions(prompt: str) -> tuple[float, str, dict[str, Any]]:
    """
    Score whether a prompt contains contradictory instructions.

    Returns ``(score, explanation, metadata)`` with ``score`` in ``[0, 1]``;
    lower scores mean more detected contradiction dimensions.
    """

    clauses = _split_instruction_clauses(prompt)
    contradictions = _collect_contradictions(clauses)
    contradiction_count = len(contradictions)
    score = max(0.0, 1.0 - (_SCORE_STEP * contradiction_count))
    explanation = _build_explanation(contradictions)

    metadata: dict[str, Any] = {
        "contradiction_count": contradiction_count,
        "contradictions": contradictions,
        "instruction_clause_count": len(clauses),
    }
    return score, explanation, metadata
