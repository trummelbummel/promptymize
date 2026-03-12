from __future__ import annotations

from bs4 import BeautifulSoup, Tag


class HtmlPreprocessor:
    """Preprocess HTML into a normalized plain-text representation.

    Keeps only the main content container and removes scripts, styles and
    navigation elements. The result is suitable for use in downstream prompt
    construction.
    """

    def _pick_main_container(self, soup: BeautifulSoup) -> Tag:
        for selector in ("main", "article", '[role="main"]', "body"):
            el = soup.select_one(selector)
            if isinstance(el, Tag):
                return el
        msg = "Could not find a main content container"
        raise ValueError(msg)

    def _strip_noise(self, container: Tag) -> None:
        for selector in (
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
        ):
            for el in list(container.select(selector)):
                el.decompose()

    def html_to_text(self, html: str) -> str:
        """Convert ``html`` into a normalized plain-text representation."""

        soup = BeautifulSoup(html, "html.parser")
        container = self._pick_main_container(soup)
        self._strip_noise(container)
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


_DEFAULT_PREPROCESSOR = HtmlPreprocessor()


def html_to_text(html: str) -> str:
    """Convenience wrapper around :class:`HtmlPreprocessor` for callers."""

    return _DEFAULT_PREPROCESSOR.html_to_text(html)

