"""
Second-pass merge for context engineering: cluster semantically similar prompt-method
sections (token overlap) and consolidate each cluster with an LM call.
"""

from __future__ import annotations

import logging
import re
from collections.abc import Callable

from auto_prompt.preprocessing.preprocessing import HtmlPreprocessor

logger = logging.getLogger(__name__)

_WORD_RE = re.compile(r"[a-z]{3,}", re.I)


def _section_tokens(section: str) -> set[str]:
    """Lowercased word tokens (length >= 3) from the first ~2.5k chars."""

    return set(_WORD_RE.findall(section.lower()[:2500]))


def jaccard_similarity(a: str, b: str) -> float:
    """Jaccard index on word-token sets (cheap proxy for semantic overlap)."""

    ta, tb = _section_tokens(a), _section_tokens(b)
    if not ta or not tb:
        return 0.0
    inter = len(ta & tb)
    union = len(ta | tb)
    return inter / union if union else 0.0


def cluster_section_indices(sections: list[str], *, threshold: float) -> list[list[int]]:
    """
    Group section indices whose pairwise Jaccard similarity meets ``threshold``.

    Uses union-find; clusters are sorted by their smallest index (document order).
    """

    n = len(sections)
    parent = list(range(n))

    def find(i: int) -> int:
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(i: int, j: int) -> None:
        ri, rj = find(i), find(j)
        if ri != rj:
            parent[rj] = ri

    for i in range(n):
        for j in range(i + 1, n):
            if jaccard_similarity(sections[i], sections[j]) >= threshold:
                union(i, j)

    buckets: dict[int, list[int]] = {}
    for i in range(n):
        r = find(i)
        buckets.setdefault(r, []).append(i)
    return sorted(buckets.values(), key=min)


def _merge_cluster_texts(
    texts: list[str],
    merger: Callable[[str], str],
    max_chunk_chars: int,
    *,
    depth: int = 0,
) -> str:
    """Merge a list of Markdown sections using ``merger``; split when input is too large."""

    texts = [t.strip() for t in texts if t.strip()]
    if not texts:
        return ""
    if len(texts) == 1:
        s = texts[0]
        if len(s) <= max_chunk_chars:
            return s
        logger.warning(
            "Semantic merge: single section length %d exceeds max_chunk_chars=%d; truncating.",
            len(s),
            max_chunk_chars,
        )
        return s[:max_chunk_chars]

    combined = "\n\n---\n\n".join(texts)
    if len(combined) <= max_chunk_chars:
        return merger(combined)

    if depth > 24:
        logger.warning("Semantic merge: max recursion depth; returning truncated join.")
        return combined[:max_chunk_chars]

    mid = max(1, len(texts) // 2)
    left = _merge_cluster_texts(texts[:mid], merger, max_chunk_chars, depth=depth + 1)
    right = _merge_cluster_texts(texts[mid:], merger, max_chunk_chars, depth=depth + 1)
    combined2 = f"{left.rstrip()}\n\n---\n\n{right.lstrip()}"
    if len(combined2) <= max_chunk_chars:
        return merger(combined2)
    return _merge_cluster_texts([left, right], merger, max_chunk_chars, depth=depth + 1)


def run_semantic_merge_pass(
    merged_markdown: str,
    merger: Callable[[str], str],
    *,
    similarity_threshold: float = 0.28,
    max_chunk_chars: int = 100_000,
) -> str:
    """
    After exact dedupe, merge sections that describe overlapping prompt methods.

    1. Split on ATX headers.
    2. Cluster by Jaccard token overlap (``similarity_threshold``).
    3. For each cluster with multiple sections, call ``merger`` on the joined text
       (possibly in chunks bounded by ``max_chunk_chars``).
    4. Reassemble clusters in original order.
    """

    stripped = merged_markdown.strip()
    if not stripped:
        return ""

    sections = [s.strip() for s in HtmlPreprocessor.split_on_headers(stripped) if s.strip()]
    if len(sections) <= 1:
        return stripped

    clusters = cluster_section_indices(sections, threshold=similarity_threshold)
    out_parts: list[str] = []
    for group in clusters:
        cluster_texts = [sections[i] for i in group]
        if len(cluster_texts) == 1:
            out_parts.append(cluster_texts[0])
        else:
            merged = _merge_cluster_texts(cluster_texts, merger, max_chunk_chars)
            if merged.strip():
                out_parts.append(merged.strip())

    return "\n\n".join(out_parts).strip()
