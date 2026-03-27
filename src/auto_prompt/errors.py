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


class ConcurrencyError(AutoPromptError):
    """A concurrency or locking related failure."""

    pass


class ValidationError(AutoPromptError):
    """Invalid user input or unsupported options."""

    pass


class ResourceNotFoundError(AutoPromptError):
    """Required files, rows, or identifiers were not found."""

    pass
