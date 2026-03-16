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
        """
        Return the first matching main-content container from ``soup``.

        :param soup: Parsed HTML document to search for a main container.
        :return: The first element matching one of the main container selectors.
        :raises ValueError: If no suitable main container can be found.
        """

        for selector in _MAIN_SELECTORS:
            el = soup.select_one(selector)
            if isinstance(el, Tag):
                return el
        msg = "Could not find a main content container"
        raise ValueError(msg)

    def _strip_noise(self, container: Tag) -> None:
        """
        Remove non-content elements (scripts, navigation, etc.) from ``container``.

        :param container: Element whose subtree will be cleaned in-place.
        :return: None.
        """

        for selector in _NOISE_SELECTORS:
            for el in list(container.select(selector)):
                el.decompose()

    def _clean_container(self, html: str) -> Tag:
        """
        Parse ``html``, locate the main container, and strip noise.

        :param html: Raw HTML document to normalize.
        :return: The main content container with noise elements removed.
        :raises ValueError: If a main content container cannot be located.
        """

        soup = BeautifulSoup(html, "html.parser")
        container = self._pick_main_container(soup)
        self._strip_noise(container)
        return container

    def html_to_text(self, html: str) -> str:
        """
        Convert ``html`` into a normalized plain-text representation.

        :param html: Raw HTML document to convert.
        :return: Plain-text content with duplicate lines collapsed and a trailing newline.
        """

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
        """
        Convert ``html`` into a normalized Markdown representation.

        :param html: Raw HTML document to convert.
        :return: Markdown content with normalized newlines and a trailing newline.
        """

        container = self._clean_container(html)
        md = html_to_md(str(container), heading_style="ATX", code_language_callback=lambda _: "")
        return md.replace("\r\n", "\n").strip() + "\n"

    @staticmethod
    def split_on_headers(markdown: str) -> list[str]:
        """
        Split ``markdown`` into sections, cutting before each header line (``# …``).

        :param markdown: Markdown text that may contain ATX-style headers.
        :return: List of non-empty sections starting at each detected header.
        """

        sections = _HEADER_RE.split(markdown)
        return [s.strip() for s in sections if s.strip()]


_DEFAULT_PREPROCESSOR = HtmlPreprocessor()


def html_to_text(html: str) -> str:
    """
    Convert HTML into normalized plain text using the default preprocessor.

    :param html: Raw HTML document to convert.
    :return: Plain-text content produced by the shared ``HtmlPreprocessor`` instance.
    """

    return _DEFAULT_PREPROCESSOR.html_to_text(html)


def html_to_markdown(html: str) -> str:
    """
    Convert HTML into normalized Markdown using the default preprocessor.

    :param html: Raw HTML document to convert.
    :return: Markdown content produced by the shared ``HtmlPreprocessor`` instance.
    """

    return _DEFAULT_PREPROCESSOR.html_to_markdown(html)

