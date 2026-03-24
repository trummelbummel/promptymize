"""Shared exception types for public APIs."""

from __future__ import annotations


class AutoPromptError(Exception):
    """Base class for recoverable, user-facing errors."""

    pass


class ConfigurationError(AutoPromptError):
    """Missing or invalid configuration (e.g. Braintrust env when eval is requested)."""

    pass


class DependencyUnavailableError(AutoPromptError):
    """Upstream dependency failed (e.g. Braintrust API)."""

    pass
