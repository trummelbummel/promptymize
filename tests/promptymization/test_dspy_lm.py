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


