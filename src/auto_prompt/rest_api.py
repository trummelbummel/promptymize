from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from auto_prompt.errors import ConfigurationError, DependencyUnavailableError, ResourceNotFoundError, ValidationError
from auto_prompt.prompt_optimizer.agent import COSTAR_FIELDS, PromptOptimizerAgent
from auto_prompt.prompt_scorer import ComparisonResult, PromptScorer, ScoreResult


@dataclass
class SessionState:
    session_id: str
    model_type: str
    agent: PromptOptimizerAgent
    messages: list[dict[str, str]] = field(default_factory=list)
    step_history: list[dict[str, Any]] = field(default_factory=list)
    uploads: list[dict[str, Any]] = field(default_factory=list)


class ScorerAdapterForAgent:
    """Adapter from agent protocol to PromptScorer API."""

    def __init__(self, scorer: PromptScorer, context_path: Path | None) -> None:
        self._scorer = scorer
        self._context_path = context_path

    def score(self, *, prompt: str, scoring_phase: str, model_type: str, session_id: str | None = None) -> object:
        return self._scorer.score(
            prompt,
            scoring_phase=scoring_phase,  # type: ignore[arg-type]
            scorer_name="keyword_alignment",
            model_type=model_type,
            context_path=self._context_path,
            session_id=session_id,
            emit_stepwise_eval=True,
        )


class RestApiService:
    """
    In-process REST backend service with canonical route handlers.

    Route names match the user-interface design doc and can be wired to a real
    web framework adapter later.
    """

    def __init__(self, *, context_path: Path | None = None) -> None:
        self.context_path = context_path
        self._scorer = PromptScorer()
        self._sessions: dict[str, SessionState] = {}

    def handle(self, *, method: str, path: str, body: dict[str, Any] | None = None) -> tuple[int, dict[str, Any]]:
        body = body or {}
        method = method.upper().strip()
        if method != "POST":
            return 405, {"error_code": "METHOD_NOT_ALLOWED", "message": "Only POST is supported.", "detail": {}}

        try:
            if path == "/v1/sessions":
                return 200, self._create_session(body)
            if path.endswith("/messages") and path.startswith("/v1/sessions/"):
                session_id = path.split("/")[3]
                return 200, self._post_message(session_id, body)
            if path.startswith("/v1/steps/") and path.endswith("/execute"):
                step_id = path.split("/")[3]
                return 200, self._execute_step(step_id, body)
            if path.startswith("/v1/steps/") and path.endswith("/rerun"):
                step_id = path.split("/")[3]
                return 200, self._rerun_step(step_id, body)
            if path == "/v1/scoring/score":
                return 200, self._score(body)
            if path == "/v1/scoring/compare":
                return 200, self._compare(body)
            if path == "/v1/uploads/datasets":
                return 200, self._upload_dataset(body)
            return 404, {"error_code": "NOT_FOUND", "message": "Route not found.", "detail": {"path": path}}
        except ValidationError as exc:
            return 400, {"error_code": "VALIDATION_ERROR", "message": str(exc), "detail": {}}
        except ResourceNotFoundError as exc:
            return 404, {"error_code": "RESOURCE_NOT_FOUND", "message": str(exc), "detail": {}}
        except ConfigurationError as exc:
            return 503, {"error_code": "CONFIGURATION_ERROR", "message": str(exc), "detail": {}}
        except DependencyUnavailableError as exc:
            return 502, {"error_code": "DEPENDENCY_UNAVAILABLE", "message": str(exc), "detail": {}}

    def _create_session(self, body: dict[str, Any]) -> dict[str, Any]:
        model_type = str(body.get("model_type", "all")).strip().lower() or "all"
        session_id = str(uuid.uuid4())
        adapter = ScorerAdapterForAgent(self._scorer, self.context_path)
        agent = PromptOptimizerAgent(model_type=model_type, context_path=self.context_path, scorer=adapter)
        self._sessions[session_id] = SessionState(session_id=session_id, model_type=model_type, agent=agent)
        return {"session_id": session_id, "model_type": model_type}

    def _post_message(self, session_id: str, body: dict[str, Any]) -> dict[str, Any]:
        session = self._get_session(session_id)
        message = str(body.get("message", "")).strip()
        if not message:
            raise ValidationError("message is required")
        session.messages.append({"role": "user", "content": message})
        reply = "Message received. Use step routes to execute agent/scoring actions."
        session.messages.append({"role": "assistant", "content": reply})
        return {"session_id": session_id, "reply": reply}

    def _execute_step(self, step_id: str, body: dict[str, Any]) -> dict[str, Any]:
        session = self._get_session(str(body.get("session_id", "")).strip())
        payload = dict(body.get("payload", {}) or {})
        result: dict[str, Any]

        if step_id == "costar_extend":
            objectives = str(payload.get("objectives", "")).strip()
            current_answers = dict(payload.get("current_answers", {}) or {})
            if not objectives:
                raise ValidationError("objectives is required")
            for key in COSTAR_FIELDS:
                if not str(current_answers.get(key, "")).strip():
                    raise ValidationError(f"CO-STAR field {key!r} is required")
            draft = session.agent.generate_costar_extension(
                objectives=objectives,
                current_answers=current_answers,
                extension_generator=lambda p: self._rules_based_costar_extension(session.agent, p),
            )
            result = {"draft": draft.fields, "objectives": draft.objectives}
        elif step_id == "apply_extension":
            edited_fields = payload.get("edited_fields")
            session.agent.approve_costar_extension(edited_fields=edited_fields if isinstance(edited_fields, dict) else None)
            updated_prompt = session.agent.apply_verified_extension(user_prompt=str(payload.get("user_prompt", "")).strip())
            result = {"updated_prompt": updated_prompt}
        elif step_id == "score":
            result = {"score_result": self._score_result_to_json(self._score_internal(session, payload))}
        elif step_id == "compare":
            result = {"comparison_result": self._comparison_result_to_json(self._compare_internal(session, payload))}
        else:
            raise ValidationError("Unsupported step_id")

        session.step_history.append({"step_id": step_id, "payload": payload, "result": result})
        return {"session_id": session.session_id, "step_id": step_id, "result": result}

    def _rerun_step(self, step_id: str, body: dict[str, Any]) -> dict[str, Any]:
        session = self._get_session(str(body.get("session_id", "")).strip())
        overrides = dict(body.get("overrides", {}) or {})
        history = [h for h in session.step_history if h["step_id"] == step_id]
        if not history:
            raise ResourceNotFoundError("No previous execution found for this step.")
        last = history[-1]
        payload = dict(last["payload"])
        payload.update(overrides)
        return self._execute_step(step_id, {"session_id": session.session_id, "payload": payload})

    def _score(self, body: dict[str, Any]) -> dict[str, Any]:
        session = self._get_session(str(body.get("session_id", "")).strip())
        payload = dict(body.get("payload", {}) or {})
        res = self._score_internal(session, payload)
        return {"session_id": session.session_id, "score_result": self._score_result_to_json(res)}

    def _compare(self, body: dict[str, Any]) -> dict[str, Any]:
        session = self._get_session(str(body.get("session_id", "")).strip())
        payload = dict(body.get("payload", {}) or {})
        res = self._compare_internal(session, payload)
        return {"session_id": session.session_id, "comparison_result": self._comparison_result_to_json(res)}

    def _upload_dataset(self, body: dict[str, Any]) -> dict[str, Any]:
        session = self._get_session(str(body.get("session_id", "")).strip())
        filename = str(body.get("filename", "")).strip()
        rows = body.get("rows")
        if not filename:
            raise ValidationError("filename is required")
        if not isinstance(rows, list):
            raise ValidationError("rows must be a list")
        upload_id = str(uuid.uuid4())
        item = {"upload_id": upload_id, "filename": filename, "rows": rows}
        session.uploads.append(item)
        return {"session_id": session.session_id, "upload_id": upload_id, "row_count": len(rows)}

    def _score_internal(self, session: SessionState, payload: dict[str, Any]) -> ScoreResult:
        prompt = str(payload.get("prompt", "")).strip()
        phase = str(payload.get("scoring_phase", "")).strip()
        scorer_name = str(payload.get("scorer_name", "keyword_alignment")).strip()
        dataset = payload.get("dataset")
        method_id = payload.get("method_id")
        return self._scorer.score(
            prompt,
            scoring_phase=phase,  # type: ignore[arg-type]
            scorer_name=scorer_name,
            model_type=session.model_type,
            context_path=self.context_path,
            dataset=dataset if isinstance(dataset, list) else None,
            method_id=str(method_id).strip() if method_id is not None else None,
            session_id=session.session_id,
            emit_stepwise_eval=True,
        )

    def _compare_internal(self, session: SessionState, payload: dict[str, Any]) -> ComparisonResult:
        before = str(payload.get("prompt_before", "")).strip()
        after = str(payload.get("prompt_after", "")).strip()
        scorer_name = str(payload.get("scorer_name", "keyword_alignment")).strip()
        dataset = payload.get("dataset")
        method_id = payload.get("method_id")
        return self._scorer.compare(
            before,
            after,
            scorer_name=scorer_name,
            model_type=session.model_type,
            context_path=self.context_path,
            dataset=dataset if isinstance(dataset, list) else None,
            method_id=str(method_id).strip() if method_id is not None else None,
            session_id=session.session_id,
            emit_stepwise_eval=True,
        )

    def _get_session(self, session_id: str) -> SessionState:
        if not session_id:
            raise ValidationError("session_id is required")
        session = self._sessions.get(session_id)
        if session is None:
            raise ResourceNotFoundError("session not found")
        return session

    def _rules_based_costar_extension(self, agent: PromptOptimizerAgent, payload: dict[str, str]) -> dict[str, str]:
        """
        Expand each CO-STAR answer into a more verbose form using task objectives and
        prompt-method context from ``prompt_methods_context.csv`` (when available).
        """

        ctx = ""
        try:
            ctx = agent.load_context_markdown()
        except Exception:
            pass
        max_excerpt = 1800
        excerpt = (ctx[:max_excerpt] + "…") if len(ctx) > max_excerpt else ctx
        objectives = payload.get("objectives", "").strip()
        out: dict[str, str] = {}
        for key in COSTAR_FIELDS:
            base = str(payload.get(key, "")).strip()
            lines = [
                base,
                "",
                f"**Elaboration:** Operationalize the **{key}** dimension for: {objectives}",
            ]
            if excerpt.strip():
                lines.extend(["", "**Grounding (prompt-method rules excerpt):**", excerpt])
            else:
                lines.append("**Grounding:** No prompt-method context loaded (missing or empty CSV).")
            out[key] = "\n".join(lines).strip()
        return out

    def _score_result_to_json(self, result: ScoreResult) -> dict[str, Any]:
        return {
            "score": result.score,
            "explanation": result.explanation,
            "scorer_name": result.scorer_name,
            "scoring_phase": result.scoring_phase,
            "metadata": result.metadata,
        }

    def _comparison_result_to_json(self, result: ComparisonResult) -> dict[str, Any]:
        return {
            "before": self._score_result_to_json(result.before),
            "after": self._score_result_to_json(result.after),
            "delta": result.delta,
            "explanation": result.explanation,
            "metadata": result.metadata,
        }

