"""Create and configure DSPy language model from environment variables."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Final

import dspy

from auto_prompt.errors import ConfigurationError

_DSPY_MODEL: Final[str] = "DSPY_MODEL"
_DSPY_API_BASE: Final[str] = "DSPY_API_BASE"
_DSPY_API_KEY: Final[str] = "DSPY_API_KEY"


def _strip_env_value(raw: str) -> str:
    """
    Normalize a value from a dotenv-like file.

    Supports:
    - quoted values: "http://..." or 'http://...'
    - trailing commas from accidental YAML/CSV-style edits
    """

    value = raw.strip()
    if value.endswith(","):
        value = value[:-1].rstrip()
    if len(value) >= 2 and ((value[0] == value[-1]) and value[0] in {"'", '"'}):
        value = value[1:-1].strip()
    return value


def _load_dspy_env_from_file(path: Path) -> None:
    """
    Load DSPY_* defaults from a dotenv-like file.

    This only sets variables that are missing or empty in ``os.environ``.
    """

    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue

        key, val = line.split("=", 1)
        key = key.strip()
        if not key.startswith("DSPY_"):
            continue

        val = _strip_env_value(val)
        if not os.environ.get(key):
            os.environ[key] = val


def _load_dspy_env_defaults() -> None:
    """
    Populate missing DSPY_* env vars from project `.env` or `.env.example`.
    """

    project_root = Path(__file__).resolve().parents[3]
    _load_dspy_env_from_file(project_root / ".env")
    # Fall back to defaults that exist in repo.
    _load_dspy_env_from_file(project_root / ".env.example")


def normalize_dspy_model(model: str, *, api_base: str) -> str:
    """
    Normalize ``DSPY_MODEL`` into a LiteLLM-friendly model string.

    dspy passes ``model=...`` directly to LiteLLM. If the user provides only a model
    name (no provider prefix like ``ollama/``), we infer the prefix from ``DSPY_API_BASE``.
    """

    model = model.strip()
    if "/" in model:
        return model

    api_base_lower = api_base.lower()
    if "11434" in api_base_lower:
        # Default in this repo: Ollama running on localhost:11434.
        return f"ollama/{model}"

    # Best-effort fallback: leave as-is.
    return model


def create_dspy_lm_from_env() -> dspy.LM:
    """
    Create a :class:`dspy.LM` using ``.env.example`` variables.

    :raises ConfigurationError: if any required DSPY env var is missing.
    """

    _load_dspy_env_defaults()

    temperature_raw = os.environ.get("DSPY_TEMPERATURE", "0.0").strip()
    try:
        temperature = float(temperature_raw)
    except ValueError:
        temperature = 0.0

    max_tokens_raw = os.environ.get("DSPY_MAX_TOKENS", "256").strip()
    try:
        max_tokens = int(max_tokens_raw)
    except ValueError:
        max_tokens = 256
    model = os.environ.get(_DSPY_MODEL, "").strip()

    if not model:
        raise ConfigurationError()

    # Prefer using DSPY_API_KEY for Groq when no explicit DSPY_API_BASE is set;
    # fall back to GROQ_API_KEY for backward compatibility.
    groq_api_key = ""
    if not os.environ.get(_DSPY_API_BASE, "").strip():
        groq_api_key = os.environ.get(_DSPY_API_KEY, "").strip() or os.environ.get("GROQ_API_KEY", "").strip()
    if groq_api_key:
        # Prefer DSPy's native Groq client when GROQ_API_KEY is provided.
        try:
            return dspy.GROQ(  # type: ignore[attr-defined]
                model=model,
                api_key=groq_api_key,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        except AttributeError as exc:
            try:
                return dspy.GroqLM(  # type: ignore[attr-defined]
                    model=model,
                    api_key=groq_api_key,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
            except AttributeError:
                # Groq client not available in this DSPy build; configure Groq via LiteLLM/OpenAI-compatible API.
                groq_api_base = os.environ.get("GROQ_API_BASE", "").strip() or "https://api.groq.com/openai/v1"
                return dspy.LM(
                    model,
                    model_type="chat",
                    temperature=temperature,
                    max_tokens=max_tokens,
                    api_base=groq_api_base,
                    api_key=groq_api_key,
                )

    api_base = os.environ.get(_DSPY_API_BASE, "").strip()
    api_key = os.environ.get(_DSPY_API_KEY, "").strip()

    if not api_base:
        raise ConfigurationError()
    if not api_key:
        raise ConfigurationError()

    litellm_model = normalize_dspy_model(model, api_base=api_base)

    # Ollama expects endpoints under the root (e.g. /api/generate).
    # If users specify ".../v1", LiteLLM/DSPy can end up calling
    # ".../v1/api/generate" which returns 404.
    api_base = api_base.rstrip("/")
    if litellm_model.startswith("ollama/") and api_base.endswith("/v1"):
        api_base = api_base[: -len("/v1")]
    # dspy defaults to ``model_type='chat'``; we spell it out for clarity.
    return dspy.LM(
        litellm_model,
        model_type="chat",
        temperature=temperature,
        max_tokens=max_tokens,
        api_base=api_base,
        api_key=api_key,
    )


def configure_dspy_lm_from_env(*, force: bool = False) -> None:
    """
    Configure global DSPy ``lm`` from environment variables.

    :param force: If true, overwrite any existing ``dspy.settings.lm``.
    """

    if not force and getattr(dspy.settings, "lm", None) is not None:
        return

    dspy.settings.configure(lm=create_dspy_lm_from_env())

