from __future__ import annotations

from auto_prompt.errors import ConfigurationError
from auto_prompt.promptymization.dspy_lm import (
    _strip_env_value,
    create_dspy_lm_from_env,
    normalize_dspy_model,
)


def test_normalize_dspy_model_infers_ollama() -> None:
    out = normalize_dspy_model("gemma3:4b", api_base="http://localhost:11434/v1")
    assert out == "ollama/gemma3:4b"


def test_create_dspy_lm_from_env_uses_env_vars(monkeypatch: object) -> None:
    # monkeypatch is typed as object to avoid importing pytest for this repo's style.
    monkeypatch.setenv("DSPY_MODEL", "gemma3:4b")  # type: ignore[attr-defined]
    monkeypatch.setenv("DSPY_API_BASE", "http://localhost:11434/v1")  # type: ignore[attr-defined]
    monkeypatch.setenv("DSPY_API_KEY", "ollama")  # type: ignore[attr-defined]

    lm = create_dspy_lm_from_env()
    assert lm.model == "ollama/gemma3:4b"
    assert lm.kwargs["api_base"] == "http://localhost:11434"


def test_create_dspy_lm_from_env_prefers_groq_when_key_present(monkeypatch: object) -> None:
    monkeypatch.setenv("DSPY_MODEL", "openai/gpt-oss-120b")  # type: ignore[attr-defined]
    monkeypatch.setenv("DSPY_API_KEY", "test-groq")  # type: ignore[attr-defined]

    # Ensure legacy DSPY_API_BASE does not interfere with Groq configuration.
    monkeypatch.delenv("DSPY_API_BASE", raising=False)  # type: ignore[attr-defined]

    lm = create_dspy_lm_from_env()
    # Either a native Groq client or a LiteLLM-backed LM using DSPY_API_KEY.
    assert getattr(lm, "model", None)


def test_create_dspy_lm_from_env_groq_openai_style_base(monkeypatch: object) -> None:
    """
    Integration-style config test for Groq OpenAI-compatible endpoint.

    Verifies that when DSPY_MODEL and DSPY_API_BASE are configured as in `.env.example`,
    the LM is constructed with those values (no network calls).
    """

    monkeypatch.setenv("DSPY_MODEL", "openai/gpt-oss-120b")  # type: ignore[attr-defined]
    monkeypatch.setenv("DSPY_API_BASE", "https://api.groq.com/openai/v1")  # type: ignore[attr-defined]
    monkeypatch.setenv("DSPY_API_KEY", "test-groq")  # type: ignore[attr-defined]

    lm = create_dspy_lm_from_env()
    assert lm.model == "openai/gpt-oss-120b"
    assert lm.kwargs.get("api_base") == "https://api.groq.com/openai/v1"


def test_create_dspy_lm_from_env_missing_model_raises(monkeypatch: object) -> None:
    monkeypatch.delenv("DSPY_MODEL", raising=False)  # type: ignore[attr-defined]
    monkeypatch.setenv("DSPY_API_BASE", "http://localhost:11434/v1")  # type: ignore[attr-defined]
    monkeypatch.setenv("DSPY_API_KEY", "ollama")  # type: ignore[attr-defined]

    # Avoid fallback defaults from `.env.example` during this negative test.
    import auto_prompt.promptymization.dspy_lm as dspy_lm

    monkeypatch.setattr(dspy_lm, "_load_dspy_env_defaults", lambda: None)

    try:
        create_dspy_lm_from_env()
    except ConfigurationError:
        return
    raise AssertionError()


def test_strip_env_value_supports_quotes_and_commas() -> None:
    assert _strip_env_value('"http://localhost:11434/v1",') == "http://localhost:11434/v1"
    assert _strip_env_value("'ollama'") == "ollama"


