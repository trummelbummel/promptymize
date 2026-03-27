from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from auto_prompt.rest_api import RestApiService


def _write_context_csv(path: Path) -> None:
    path.write_text(
        "method_name,model_type,section_markdown\n"
        "\"Universal\",\"all\",\"## Universal\n- State output format clearly\"\n"
        "\"GPT JSON\",\"gpt\",\"## GPT JSON\n- Ask for JSON schema\"\n",
        encoding="utf-8",
    )


def test_rest_api_session_and_message_flow(tmp_path: Path) -> None:
    context_path = tmp_path / "prompt_methods_context.csv"
    _write_context_csv(context_path)
    api = RestApiService(context_path=context_path)

    code, body = api.handle(method="POST", path="/v1/sessions", body={"model_type": "gpt"})
    assert code == 200
    sid = body["session_id"]

    code, body = api.handle(
        method="POST",
        path=f"/v1/sessions/{sid}/messages",
        body={"message": "hello"},
    )
    assert code == 200
    assert "reply" in body


def test_rest_api_step_execute_and_rerun(tmp_path: Path) -> None:
    context_path = tmp_path / "prompt_methods_context.csv"
    _write_context_csv(context_path)
    api = RestApiService(context_path=context_path)
    _, session = api.handle(method="POST", path="/v1/sessions", body={"model_type": "gpt"})
    sid = session["session_id"]

    code, resp = api.handle(
        method="POST",
        path="/v1/steps/costar_extend/execute",
        body={
            "session_id": sid,
            "payload": {"objectives": "improve output quality", "current_answers": {"objective": "summarize"}},
        },
    )
    assert code == 200
    assert "draft" in resp["result"]

    code, resp = api.handle(
        method="POST",
        path="/v1/steps/costar_extend/rerun",
        body={"session_id": sid, "overrides": {"objectives": "optimize for executives"}},
    )
    assert code == 200
    assert resp["step_id"] == "costar_extend"


def test_rest_api_scoring_routes(tmp_path: Path) -> None:
    context_path = tmp_path / "prompt_methods_context.csv"
    _write_context_csv(context_path)
    api = RestApiService(context_path=context_path)
    _, session = api.handle(method="POST", path="/v1/sessions", body={"model_type": "gpt"})
    sid = session["session_id"]

    with patch("auto_prompt.prompt_scorer.run_step_eval"):
        code, score_body = api.handle(
            method="POST",
            path="/v1/scoring/score",
            body={
                "session_id": sid,
                "payload": {
                    "prompt": "Use JSON schema output format",
                    "scoring_phase": "before",
                    "scorer_name": "keyword_alignment",
                },
            },
        )
        assert code == 200
        assert "score_result" in score_body

        code, compare_body = api.handle(
            method="POST",
            path="/v1/scoring/compare",
            body={
                "session_id": sid,
                "payload": {
                    "prompt_before": "Summarize this text",
                    "prompt_after": "Summarize this text with explicit JSON schema",
                    "scorer_name": "keyword_alignment",
                },
            },
        )
        assert code == 200
        assert "comparison_result" in compare_body
        assert "delta" in compare_body["comparison_result"]


def test_rest_api_upload_route(tmp_path: Path) -> None:
    context_path = tmp_path / "prompt_methods_context.csv"
    _write_context_csv(context_path)
    api = RestApiService(context_path=context_path)
    _, session = api.handle(method="POST", path="/v1/sessions", body={"model_type": "gpt"})
    sid = session["session_id"]

    code, body = api.handle(
        method="POST",
        path="/v1/uploads/datasets",
        body={
            "session_id": sid,
            "filename": "dataset.json",
            "rows": [{"input": "x", "expected_keywords": ["json", "schema"]}],
        },
    )
    assert code == 200
    assert body["row_count"] == 1

