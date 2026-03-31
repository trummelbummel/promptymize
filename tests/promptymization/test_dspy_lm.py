from __future__ import annotations

from pathlib import Path

from auto_prompt.errors import ConfigurationError
from auto_prompt.promptymization.dspy_lm import (
    _read_dspy_config_from_env_file,
    _strip_env_value,
    create_dspy_lm_from_env,
)


def test_read_dspy_config_from_env_file(tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        'DSPY_MODEL="openai/gpt-oss-120b"\n'
        'DSPY_API_BASE="https://api.groq.com/openai/v1"\n'
        'DSPY_TEMPERATURE="0.1"\n',
        encoding="utf-8",
    )
    cfg = _read_dspy_config_from_env_file(env_file)
    assert cfg["DSPY_MODEL"] == "openai/gpt-oss-120b"
    assert cfg["DSPY_API_BASE"] == "https://api.groq.com/openai/v1"
    assert cfg["DSPY_TEMPERATURE"] == "0.1"


def test_create_dspy_lm_from_env_uses_dotenv_and_api_key_env(monkeypatch: object, tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        'DSPY_MODEL="openai/gpt-oss-120b"\n'
        'DSPY_API_BASE="https://api.groq.com/openai/v1"\n'
        'DSPY_TEMPERATURE="0.0"\n'
        'DSPY_MAX_TOKENS="256"\n',
        encoding="utf-8",
    )
    import auto_prompt.promptymization.dspy_lm as dspy_lm

    monkeypatch.setattr(dspy_lm, "_project_env_path", lambda: env_file)
    monkeypatch.setenv("DSPY_API_KEY", "test-groq")  # type: ignore[attr-defined]

    lm = create_dspy_lm_from_env()
    assert lm.model == "openai/gpt-oss-120b"
    assert lm.kwargs.get("api_base") == "https://api.groq.com/openai/v1"


def test_create_dspy_lm_from_env_missing_model_raises(monkeypatch: object) -> None:
    env_file = Path("/tmp/nonexistent-test-env")
    import auto_prompt.promptymization.dspy_lm as dspy_lm

    monkeypatch.setattr(dspy_lm, "_project_env_path", lambda: env_file)
    monkeypatch.setenv("DSPY_API_KEY", "test-groq")  # type: ignore[attr-defined]

    try:
        create_dspy_lm_from_env()
    except ConfigurationError:
        return
    raise AssertionError()


def test_strip_env_value_supports_quotes_and_commas() -> None:
    assert _strip_env_value('"http://localhost:11434/v1",') == "http://localhost:11434/v1"
    assert _strip_env_value("'ollama'") == "ollama"


