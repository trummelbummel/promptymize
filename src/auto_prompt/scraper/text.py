"""Re-export preprocessing symbols for backward-compatible ``auto_prompt.scraper.text`` imports."""

from __future__ import annotations

from auto_prompt.preprocessing.preprocessing import HtmlPreprocessor, html_to_markdown, html_to_text

__all__ = ["HtmlPreprocessor", "html_to_markdown", "html_to_text"]

