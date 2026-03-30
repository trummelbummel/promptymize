"""Load Braintrust configuration from the environment."""

from __future__ import annotations

import os
from dataclasses import dataclass

from auto_prompt.errors import ConfigurationError


@dataclass(frozen=True, slots=True)
class BraintrustConfig:
    """
    Credentials and project scope for Braintrust logging.

    :param api_key: API key (never commit; use env).
    :param project_id: Optional Braintrust project id (takes precedence over name when set).
    :param project_name: Human-readable project name when ``project_id`` is not set.
    """

    api_key: str
    project_id: str | None
    project_name: str


def load_braintrust_config_from_env() -> BraintrustConfig:
    """
    Read Braintrust settings from process environment.

    :return: Validated configuration.
    :raises ConfigurationError: If ``BRAINTRUST_API_KEY`` is missing or empty.
    """

    key = os.environ.get("BRAINTRUST_API_KEY", "").strip()
    if not key:
        raise ConfigurationError(
            "BRAINTRUST_API_KEY is required when stepwise evaluation is enabled. See .env.example.",
        )
    project_id = os.environ.get("BRAINTRUST_PROJECT_ID", "").strip() or None
    project_name = os.environ.get("BRAINTRUST_PROJECT_NAME", "promptymize").strip() or "promptymize"
    return BraintrustConfig(api_key=key, project_id=project_id, project_name=project_name)
