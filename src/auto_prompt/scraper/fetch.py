from __future__ import annotations

from typing import Final

import requests

from auto_prompt.preprocessing.preprocessing import HtmlPreprocessor

USER_AGENT: Final = "auto-prompt-web-scraper/0.0.1 (+https://github.com/trummelbummel/auto-prompt)"

_MIN_PLAYWRIGHT_TIMEOUT_S: Final = 45.0
_MAX_SHELL_LINES: Final = 30
_MIN_CONTENT_LENGTH: Final = 400


class HtmlFetcher:
    """
    Fetch HTML for a URL, with optional JS rendering fallback.

    :param preprocessor: Optional HTML preprocessor used to inspect responses.
    """

    def __init__(self, preprocessor: HtmlPreprocessor | None = None) -> None:
        """
        Initialize a new :class:`HtmlFetcher` instance.

        :param preprocessor: Optional HTML preprocessor used to inspect responses.
        """

        self._preprocessor = preprocessor or HtmlPreprocessor()

    def _fetch_via_requests(self, url: str, *, timeout_s: float = 30.0) -> str:
        """
        Perform a plain HTTP GET and return the response body.

        :param url: URL to fetch.
        :param timeout_s: Request timeout in seconds.
        :return: Response body decoded as text.
        :raises requests.HTTPError: If the response status is not successful.
        """

        headers = {
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml",
        }
        resp = requests.get(url, headers=headers, timeout=timeout_s)
        resp.raise_for_status()
        resp.encoding = resp.encoding or "utf-8"
        return resp.text

    def _fetch_via_playwright(self, url: str, *, timeout_s: float = 45.0) -> str:
        """
        Launch a headless browser, wait for the page to settle, and return HTML.

        :param url: URL to fetch with a headless browser.
        :param timeout_s: Overall navigation timeout in seconds.
        :return: Rendered page HTML as a string.
        """

        from playwright.sync_api import sync_playwright  # type: ignore[import-not-found]

        timeout_ms = int(timeout_s * 1000)
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            try:
                page = browser.new_page()
                page.goto(url, wait_until="networkidle", timeout=timeout_ms)
                return page.content()
            finally:
                browser.close()

    def _looks_like_unrendered_shell(self, text: str) -> bool:
        """
        Return ``True`` when ``text`` appears to be a JS-only loading stub.

        :param text: Textual representation of the page content.
        :return: ``True`` when the content is likely just a loading shell.
        """

        nonempty = [line.strip() for line in text.splitlines() if line.strip()]
        if len(nonempty) <= _MAX_SHELL_LINES and any(line.lower() == "loading..." for line in nonempty):
            return True
        return len(text.strip()) < _MIN_CONTENT_LENGTH

    def fetch_html(self, url: str, *, timeout_s: float = 30.0, render_js: bool = True) -> str:
        """
        Fetch HTML for ``url``, optionally falling back to a JS-rendered snapshot.

        :param url: URL to fetch.
        :param timeout_s: Request timeout in seconds for the initial fetch.
        :param render_js: When ``True``, fall back to JS-rendered HTML when needed.
        :return: HTML string for the requested URL.
        """

        html = self._fetch_via_requests(url, timeout_s=timeout_s)
        if not render_js:
            return html

        try:
            text = self._preprocessor.html_to_text(html)
        except Exception:
            text = ""

        if not self._looks_like_unrendered_shell(text):
            return html
        return self._fetch_via_playwright(url, timeout_s=max(timeout_s, _MIN_PLAYWRIGHT_TIMEOUT_S))


_DEFAULT_FETCHER = HtmlFetcher()


def fetch_html(url: str, *, timeout_s: float = 30.0, render_js: bool = True) -> str:
    """
    Fetch HTML for a URL using the shared default :class:`HtmlFetcher`.

    :param url: URL to fetch.
    :param timeout_s: Request timeout in seconds for the initial fetch.
    :param render_js: When ``True``, fall back to JS-rendered HTML when needed.
    :return: HTML string for the requested URL.
    """

    return _DEFAULT_FETCHER.fetch_html(url=url, timeout_s=timeout_s, render_js=render_js)
