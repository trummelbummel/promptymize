"""Placeholder trace shape for future agent + UI end-to-end evaluation."""

from __future__ import annotations

from typing import Any, TypedDict


class EndToEndTraceStub(TypedDict, total=False):
    """
    Minimal JSON-serializable stub for an end-to-end session trace.

    Populated by future agent/UI integration; kept stable for step registry tests.
    """

    session_id: str
    user_prompt_excerpt: str
    agent_turns: int
    scorer_invocations: int
    notes: str


def build_end_to_end_stub(
    *,
    session_id: str = "stub-session",
    user_prompt_excerpt: str = "",
) -> EndToEndTraceStub:
    """
    Return a placeholder trace for wiring and tests.

    :param session_id: Correlation id.
    :param user_prompt_excerpt: Short prompt snippet.
    :return: Stub mapping.
    """

    return {
        "session_id": session_id,
        "user_prompt_excerpt": user_prompt_excerpt,
        "agent_turns": 0,
        "scorer_invocations": 0,
        "notes": "stub — replace when prompt-optimizer-agent + UI land",
    }


def trace_to_jsonable(trace: EndToEndTraceStub) -> dict[str, Any]:
    """
    Return a plain dict for logging (Braintrust rows).

    :param trace: Stub or future real trace.
    :return: JSON-serializable dict.
    """

    return dict(trace)

