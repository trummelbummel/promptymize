"""Heuristic scoring for contradictory prompt instructions."""

from __future__ import annotations

import re
from typing import Any

_SPLIT_RE = re.compile(r"[\n\r]+|[.;]+")

_CONTRADICTION_RULES: tuple[dict[str, Any], ...] = (
    {
        "dimension": "verbosity",
        "positive_label": "concise/brief",
        "negative_label": "detailed/comprehensive",
        "positive": re.compile(r"\b(concise|brief|short|succinct)\b", re.I),
        "negative": re.compile(r"\b(detailed|comprehensive|in[\s-]?depth|thorough)\b", re.I),
    },
    {
        "dimension": "length",
        "positive_label": "long output",
        "negative_label": "very short output",
        "positive": re.compile(r"\b(long|extensive|at least \d+ (?:words|paragraphs|pages))\b", re.I),
        "negative": re.compile(r"\b(one sentence|single sentence|under \d+ words|very short)\b", re.I),
    },
    {
        "dimension": "format",
        "positive_label": "use bullet points",
        "negative_label": "avoid bullet points",
        "positive": re.compile(r"\b(use|include|write in)\b.*\b(bullets?|bullet points?)\b", re.I),
        "negative": re.compile(r"\b(no|avoid|without)\b.*\b(bullets?|bullet points?)\b", re.I),
    },
    {
        "dimension": "code",
        "positive_label": "include code",
        "negative_label": "no code",
        "positive": re.compile(r"\b(include|show|provide)\b.*\b(code|snippet)\b", re.I),
        "negative": re.compile(r"\b(no|avoid|without|do not)\b.*\b(code|snippet)\b", re.I),
    },
    {
        "dimension": "certainty",
        "positive_label": "be certain",
        "negative_label": "state uncertainty",
        "positive": re.compile(r"\b(definitive|certain|confident|always)\b", re.I),
        "negative": re.compile(r"\b(uncertain|maybe|might|unknown|depends)\b", re.I),
    },
)


def _split_instruction_clauses(prompt: str) -> list[str]:
    clauses: list[str] = []
    for chunk in _SPLIT_RE.split(prompt):
        cleaned = " ".join(chunk.strip().split())
        if cleaned:
            clauses.append(cleaned)
    return clauses


def score_instruction_contradictions(prompt: str) -> tuple[float, str, dict[str, Any]]:
    """
    Score whether a prompt contains contradictory instructions.

    Returns a tuple of ``(score, explanation, metadata)`` where score is in ``[0, 1]``
    and lower values indicate more contradictory instructions.
    """

    clauses = _split_instruction_clauses(prompt)
    contradictions: list[dict[str, Any]] = []

    for rule in _CONTRADICTION_RULES:
        positive_hits = [c for c in clauses if rule["positive"].search(c)]
        negative_hits = [c for c in clauses if rule["negative"].search(c)]
        if positive_hits and negative_hits:
            contradictions.append(
                {
                    "dimension": rule["dimension"],
                    "positive_instruction": rule["positive_label"],
                    "negative_instruction": rule["negative_label"],
                    "examples": {
                        "positive": positive_hits[:2],
                        "negative": negative_hits[:2],
                    },
                }
            )

    contradiction_count = len(contradictions)
    score = max(0.0, 1.0 - (0.2 * contradiction_count))

    if contradiction_count == 0:
        explanation = "No contradictory instructions were detected."
    else:
        parts = []
        for item in contradictions:
            parts.append(
                f"{item['dimension']}: '{item['positive_instruction']}' conflicts with "
                f"'{item['negative_instruction']}'"
            )
        explanation = (
            f"Detected {contradiction_count} contradictory instruction pair(s): "
            + "; ".join(parts)
            + "."
        )

    metadata: dict[str, Any] = {
        "contradiction_count": contradiction_count,
        "contradictions": contradictions,
        "instruction_clause_count": len(clauses),
    }
    return score, explanation, metadata

