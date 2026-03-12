from __future__ import annotations

import re

from bs4 import BeautifulSoup, Tag
from markdownify import markdownify as html_to_md

_HEADER_RE = re.compile(r"(?=^#{1,6}\s)", re.MULTILINE)

_NOISE_SELECTORS = (
    "script",
    "style",
    "noscript",
    "svg",
    "header",
    "footer",
    "nav",
    "aside",
    "form",
    '[aria-hidden="true"]',
)

_MAIN_SELECTORS = ("main", "article", '[role="main"]', "body")


class HtmlPreprocessor:
    """Preprocess HTML into normalized representations.

    Keeps only the main content container and removes scripts, styles and
    navigation elements. The result is suitable for use in downstream prompt
    construction, either as plain text or as lightweight Markdown.
    """

    def _pick_main_container(self, soup: BeautifulSoup) -> Tag:
        """Return the first matching main-content container from ``soup``."""

        for selector in _MAIN_SELECTORS:
            el = soup.select_one(selector)
            if isinstance(el, Tag):
                return el
        msg = "Could not find a main content container"
        raise ValueError(msg)

    def _strip_noise(self, container: Tag) -> None:
        """Remove non-content elements (scripts, nav, etc.) from ``container``."""

        for selector in _NOISE_SELECTORS:
            for el in list(container.select(selector)):
                el.decompose()

    def _clean_container(self, html: str) -> Tag:
        """Parse ``html``, locate the main container, and strip noise."""

        soup = BeautifulSoup(html, "html.parser")
        container = self._pick_main_container(soup)
        self._strip_noise(container)
        return container

    def html_to_text(self, html: str) -> str:
        """Convert ``html`` into a normalized plain-text representation."""

        container = self._clean_container(html)
        text = container.get_text(separator="\n", strip=True)
        lines = [line.strip() for line in text.splitlines()]
        collapsed: list[str] = []
        for line in lines:
            if not line:
                continue
            if collapsed and collapsed[-1] == line:
                continue
            collapsed.append(line)
        return "\n".join(collapsed).strip() + "\n"

    def html_to_markdown(self, html: str) -> str:
        """Convert ``html`` into a normalized Markdown representation."""

        container = self._clean_container(html)
        md = html_to_md(str(container), heading_style="ATX", code_language_callback=lambda _: "")
        return md.replace("\r\n", "\n").strip() + "\n"

    @staticmethod
    def split_on_headers(markdown: str) -> list[str]:
        """Split ``markdown`` into sections, cutting before each header line (``# …``)."""

        sections = _HEADER_RE.split(markdown)
        return [s.strip() for s in sections if s.strip()]


_DEFAULT_PREPROCESSOR = HtmlPreprocessor()


def html_to_text(html: str) -> str:
    """Convenience wrapper around :class:`HtmlPreprocessor` for callers."""

    return _DEFAULT_PREPROCESSOR.html_to_text(html)


def html_to_markdown(html: str) -> str:
    """Convenience wrapper that returns Markdown instead of plain text."""

    return _DEFAULT_PREPROCESSOR.html_to_markdown(html)

