from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from auto_prompt.preprocessing.context_csv import ContextMethodRow, load_context_rows, rows_to_markdown

COSTAR_FIELDS: tuple[str, ...] = (
    "context",
    "objective",
    "style",
    "tone",
    "audience",
    "response",
)


class PromptScorerAdapter(Protocol):
    """Minimal scorer boundary for the optimizer agent."""

    def score(self, *, prompt: str, scoring_phase: str, model_type: str, session_id: str | None = None) -> object:
        """Return a scorer result object for one prompt/phase."""


@dataclass(frozen=True)
class CostarExtensionDraft:
    """Single-pass extension draft across all CO-STAR dimensions."""

    fields: dict[str, str]
    objectives: str


class PromptOptimizerAgent:
    """
    Prompt optimization orchestrator for CO-STAR extension and proposal application.

    This class enforces the user-in-the-loop gate:
    - generate one joint CO-STAR extension draft,
    - require explicit review/approval (optionally with edits),
    - only then allow application to the working prompt.
    """

    def __init__(
        self,
        *,
        model_type: str,
        context_path: Path | None = None,
        scorer: PromptScorerAdapter | None = None,
    ) -> None:
        self.model_type = model_type.strip().lower() or "all"
        self.context_path = context_path
        self.scorer = scorer
        self._pending_extension: CostarExtensionDraft | None = None
        self._approved_extension: CostarExtensionDraft | None = None

    def load_context_rows(self) -> list[ContextMethodRow]:
        """
        Load model-filtered context rows for this agent.

        Includes rows labeled ``all`` plus rows matching this agent's ``model_type``.
        """

        return load_context_rows(
            context_path=self.context_path,
            model_type=self.model_type,
            include_all_rows=True,
        )

    def load_context_markdown(self) -> str:
        """Load and collapse model-filtered context rows into markdown."""

        return rows_to_markdown(self.load_context_rows())

    def generate_costar_extension(
        self,
        *,
        objectives: str,
        current_answers: dict[str, str],
        extension_generator: Callable[[dict[str, str]], dict[str, str]],
    ) -> CostarExtensionDraft:
        """
        Create one CO-STAR extension draft with a single generator call.

        :param objectives: Free-text objectives spanning the prompt task.
        :param current_answers: User-provided CO-STAR fields (partial allowed).
        :param extension_generator: Callback performing one generation pass.
        :return: Draft stored as pending review.
        """

        payload = self._build_extension_payload(objectives=objectives, current_answers=current_answers)
        generated = extension_generator(payload)
        fields = self._normalize_costar_fields(generated)
        draft = CostarExtensionDraft(fields=fields, objectives=objectives.strip())
        self._pending_extension = draft
        self._approved_extension = None
        return draft

    def approve_costar_extension(self, *, edited_fields: dict[str, str] | None = None) -> CostarExtensionDraft:
        """
        Approve the pending extension draft (optionally with user edits).
        """

        if self._pending_extension is None:
            raise ValueError("No pending CO-STAR extension draft to approve.")

        if edited_fields:
            merged = dict(self._pending_extension.fields)
            for k, v in edited_fields.items():
                key = k.strip().lower()
                if key in COSTAR_FIELDS:
                    merged[key] = str(v).strip()
            approved = CostarExtensionDraft(
                fields=self._normalize_costar_fields(merged),
                objectives=self._pending_extension.objectives,
            )
        else:
            approved = self._pending_extension

        self._approved_extension = approved
        return approved

    def reject_costar_extension(self) -> None:
        """Reject and clear any pending/approved extension draft."""

        self._pending_extension = None
        self._approved_extension = None

    def apply_verified_extension(self, *, user_prompt: str) -> str:
        """
        Apply the approved CO-STAR extension to the working prompt.

        :raises ValueError: If no extension has been approved by the user.
        """

        if self._approved_extension is None:
            raise ValueError("Cannot apply extension before user approval.")

        base = user_prompt.strip()
        lines: list[str] = [base] if base else []
        lines.append("")
        lines.append("## CO-STAR guidance")
        for key in COSTAR_FIELDS:
            value = self._approved_extension.fields.get(key, "").strip()
            if value:
                lines.append(f"- {key}: {value}")
        return "\n".join(lines).strip() + "\n"

    def score_prompt(self, *, prompt: str, scoring_phase: str, session_id: str | None = None) -> object:
        """Delegate scoring to the configured scorer boundary."""

        if self.scorer is None:
            raise ValueError("No scorer adapter configured.")
        return self.scorer.score(
            prompt=prompt,
            scoring_phase=scoring_phase,
            model_type=self.model_type,
            session_id=session_id,
        )

    def _build_extension_payload(self, *, objectives: str, current_answers: dict[str, str]) -> dict[str, str]:
        payload: dict[str, str] = {"objectives": objectives.strip()}
        for key in COSTAR_FIELDS:
            payload[key] = str(current_answers.get(key, "")).strip()
        return payload

    def _normalize_costar_fields(self, values: dict[str, str]) -> dict[str, str]:
        out: dict[str, str] = {}
        for key in COSTAR_FIELDS:
            out[key] = str(values.get(key, "")).strip()
        return out

