"""Instantiate DSPy LM from `.env` config + runtime API key env."""

from __future__ import annotations

import os
from pathlib import Path

import dspy

from auto_prompt.errors import ConfigurationError


def _strip_env_value(raw: str) -> str:
    """Normalize one dotenv value."""
    value = raw.strip()
    if value.endswith(","):
        value = value[:-1].rstrip()
    if len(value) >= 2 and ((value[0] == value[-1]) and value[0] in {"'", '"'}):
        value = value[1:-1].strip()
    return value  # pragma: no cover


def _project_env_path() -> Path:
    """
    Return project config path, preferring `.env` and falling back to `.env.example`.
    """

    root = Path(__file__).resolve().parents[3]
    env_path = root / ".env"
    if env_path.exists():
        return env_path
    return root / ".env.example"


def _read_dspy_config_from_env_file(path: Path) -> dict[str, str]:
    """Read DSPY_* config values from dotenv file."""
    cfg: dict[str, str] = {}
    if not path.exists():
        return cfg

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue

        key, val = (part.strip() for part in line.split("=", 1))
        if not key.startswith("DSPY_") or key == "DSPY_API_KEY":
            continue
        cfg[key] = _strip_env_value(val)
    return cfg

def create_dspy_lm_from_env() -> dspy.LM:
    """Create `dspy.LM` from `.env` config and `DSPY_API_KEY` env var."""
    cfg = _read_dspy_config_from_env_file(_project_env_path())
    model = cfg.get("DSPY_MODEL", "").strip()
    api_base = cfg.get("DSPY_API_BASE", "").strip()
    api_key = os.environ.get("DSPY_API_KEY", "").strip()
    print(model, api_base, api_key)
    print('########################################################')
    if not model or not api_base or not api_key:
        raise ConfigurationError("Missing DSPY_MODEL/DSPY_API_BASE in .env or DSPY_API_KEY in environment.")
    try:
        temperature = float(cfg.get("DSPY_TEMPERATURE", "0.0"))
    except ValueError:
        temperature = 0.0
    try:
        max_tokens = int(cfg.get("DSPY_MAX_TOKENS", "256"))
    except ValueError:
        max_tokens = 256
    return dspy.LM(
        model,
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

