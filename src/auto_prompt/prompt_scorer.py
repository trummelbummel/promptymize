from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal, Protocol

from auto_prompt.errors import DependencyUnavailableError, ResourceNotFoundError, ValidationError
from auto_prompt.evaluation import run_step_eval
from auto_prompt.promptymization.context_csv import ContextMethodRow, load_context_rows, rows_to_markdown

ScoringPhase = Literal["before", "after"]


@dataclass(slots=True)
class ScoreResult:
    """Scoring output for one prompt."""

    score: float
    explanation: str
    scorer_name: str
    scoring_phase: ScoringPhase
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ComparisonResult:
    """Side-by-side score output for prompt comparison."""

    before: ScoreResult
    after: ScoreResult
    delta: float
    explanation: str
    metadata: dict[str, Any] = field(default_factory=dict)


class ScoringProfile(Protocol):
    """Interface for pluggable scoring profiles."""

    def evaluate(
        self,
        *,
        prompt: str,
        context_markdown: str,
        dataset: list[dict[str, Any]] | None = None,
    ) -> tuple[float, str, dict[str, Any]]:
        """Return (score, explanation, metadata)."""


def _tokenize(text: str) -> set[str]:
    return {t.lower() for t in re.findall(r"[a-zA-Z][a-zA-Z0-9_-]+", text)}


class KeywordAlignmentProfile:
    """
    Simple deterministic profile based on prompt-context keyword overlap.

    If dataset rows include ``expected_keywords`` (list[str] or comma-separated str),
    this profile also reports dataset keyword coverage in metadata.
    """

    def evaluate(
        self,
        *,
        prompt: str,
        context_markdown: str,
        dataset: list[dict[str, Any]] | None = None,
    ) -> tuple[float, str, dict[str, Any]]:
        prompt_tokens = _tokenize(prompt)
        context_tokens = _tokenize(context_markdown)
        overlap = prompt_tokens.intersection(context_tokens)
        denom = max(1, min(30, len(context_tokens)))
        base_score = min(1.0, len(overlap) / denom)

        dataset_cov: float | None = None
        if dataset:
            expected: set[str] = set()
            for row in dataset:
                raw = row.get("expected_keywords")
                if isinstance(raw, str):
                    expected.update(t.strip().lower() for t in raw.split(",") if t.strip())
                elif isinstance(raw, list):
                    expected.update(str(x).strip().lower() for x in raw if str(x).strip())
            if expected:
                hit = len(prompt_tokens.intersection(expected))
                dataset_cov = hit / len(expected)
                base_score = min(1.0, (base_score * 0.7) + (dataset_cov * 0.3))

        explanation = (
            f"Prompt overlaps {len(overlap)} context keywords "
            f"out of an effective {denom} keyword window."
        )
        meta: dict[str, Any] = {
            "overlap_count": len(overlap),
            "effective_context_window": denom,
            "matched_keywords": sorted(overlap)[:25],
        }
        if dataset_cov is not None:
            meta["dataset_keyword_coverage"] = dataset_cov
            explanation += " Dataset keyword coverage was included."

        return base_score, explanation, meta


class PromptScorer:
    """Facade for prompt scoring and comparison."""

    def __init__(self) -> None:
        self._profiles: dict[str, ScoringProfile] = {"keyword_alignment": KeywordAlignmentProfile()}

    def register(self, name: str, profile: ScoringProfile) -> None:
        """Register a scoring profile under ``name``."""

        key = name.strip().lower()
        if not key:
            raise ValidationError("Scorer profile name cannot be empty.")
        self._profiles[key] = profile

    def score(
        self,
        prompt: str,
        *,
        scoring_phase: ScoringPhase,
        scorer_name: str,
        model_type: str = "all",
        context_path: Path | None = None,
        dataset: list[dict[str, Any]] | None = None,
        method_id: str | None = None,
        session_id: str | None = None,
        emit_stepwise_eval: bool = False,
    ) -> ScoreResult:
        """Score one prompt in before/after phase."""

        prompt = prompt.strip()
        if not prompt:
            raise ValidationError("Prompt cannot be empty.")
        if scoring_phase not in {"before", "after"}:
            raise ValidationError("scoring_phase must be 'before' or 'after'.")

        profile = self._profiles.get(scorer_name.strip().lower())
        if profile is None:
            raise ValidationError("Unknown scorer profile.")

        rows = load_context_rows(
            context_path=context_path,
            model_type=model_type.strip().lower() or "all",
            include_all_rows=True,
        )
        if not rows:
            raise ResourceNotFoundError("No context rows available for requested model type.")

        selected_rows = self._select_method_rows(rows=rows, method_id=method_id)
        context_markdown = rows_to_markdown(selected_rows)
        if not context_markdown.strip():
            raise ResourceNotFoundError("Resolved context markdown is empty.")

        score_value, explanation, meta = profile.evaluate(
            prompt=prompt,
            context_markdown=context_markdown,
            dataset=dataset,
        )
        result = ScoreResult(
            score=max(0.0, min(1.0, float(score_value))),
            explanation=explanation.strip(),
            scorer_name=scorer_name.strip().lower(),
            scoring_phase=scoring_phase,
            metadata={
                "model_type": model_type.strip().lower() or "all",
                "method_id": method_id,
                "session_id": session_id,
                **meta,
            },
        )

        if emit_stepwise_eval:
            self._emit_stepwise_record(
                prompt=prompt,
                result=result,
                context_path=str(context_path) if context_path is not None else None,
                dataset_size=len(dataset or []),
                method_id=method_id,
                session_id=session_id,
            )

        return result

    def compare(
        self,
        prompt_before: str,
        prompt_after: str,
        *,
        scorer_name: str,
        model_type: str = "all",
        context_path: Path | None = None,
        dataset: list[dict[str, Any]] | None = None,
        method_id: str | None = None,
        session_id: str | None = None,
        emit_stepwise_eval: bool = False,
    ) -> ComparisonResult:
        """Score before/after prompts and return deltas."""

        before = self.score(
            prompt_before,
            scoring_phase="before",
            scorer_name=scorer_name,
            model_type=model_type,
            context_path=context_path,
            dataset=dataset,
            method_id=method_id,
            session_id=session_id,
            emit_stepwise_eval=emit_stepwise_eval,
        )
        after = self.score(
            prompt_after,
            scoring_phase="after",
            scorer_name=scorer_name,
            model_type=model_type,
            context_path=context_path,
            dataset=dataset,
            method_id=method_id,
            session_id=session_id,
            emit_stepwise_eval=emit_stepwise_eval,
        )
        delta = after.score - before.score
        explanation = (
            f"Score changed by {delta:+.3f} ({before.score:.3f} -> {after.score:.3f}) "
            "using the selected scorer profile."
        )
        return ComparisonResult(
            before=before,
            after=after,
            delta=delta,
            explanation=explanation,
            metadata={"scorer_name": scorer_name.strip().lower(), "session_id": session_id},
        )

    def _select_method_rows(
        self,
        *,
        rows: list[ContextMethodRow],
        method_id: str | None,
    ) -> list[ContextMethodRow]:
        if method_id is None or not method_id.strip():
            return rows
        wanted = method_id.strip().lower()
        selected = [r for r in rows if r.method_name.strip().lower() == wanted]
        if not selected:
            raise ResourceNotFoundError("Requested method_id is not present in context rows.")
        return selected

    def _emit_stepwise_record(
        self,
        *,
        prompt: str,
        result: ScoreResult,
        context_path: str | None,
        dataset_size: int,
        method_id: str | None,
        session_id: str | None,
    ) -> None:
        try:
            run_step_eval(
                "agent_turn",
                prompt=prompt,
                scoring_phase=result.scoring_phase,
                scorer_name=result.scorer_name,
                score=result.score,
                explanation=result.explanation,
                context_path=context_path,
                dataset_size=dataset_size,
                method_id=method_id,
                session_id=session_id,
                metadata=result.metadata,
            )
        except Exception as exc:
            raise DependencyUnavailableError("Stepwise eval logging failed.") from exc

