from __future__ import annotations

from typing import Final

import requests

from scraper.text import HtmlPreprocessor, html_to_text

USER_AGENT: Final = "auto-prompt-web-scraper/0.0.1 (+https://github.com/trummelbummel/auto-prompt)"


class HtmlFetcher:
    """Fetch HTML for a URL, with optional JS rendering fallback."""

    def __init__(self, preprocessor: HtmlPreprocessor | None = None) -> None:
        self._preprocessor = preprocessor or HtmlPreprocessor()

    def _fetch_html_requests(self, url: str, *, timeout_s: float = 30.0) -> str:
        headers = {
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml",
        }
        resp = requests.get(url, headers=headers, timeout=timeout_s)
        resp.raise_for_status()
        resp.encoding = resp.encoding or "utf-8"
        return resp.text

    def _fetch_html_playwright(self, url: str, *, timeout_s: float = 45.0) -> str:
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
        nonempty = [line.strip() for line in text.splitlines() if line.strip()]
        if len(nonempty) <= 30 and any(line.lower() == "loading..." for line in nonempty):
            return True
        if len(text.strip()) < 400:
            return True
        return False

    def fetch_html(self, url: str, *, timeout_s: float = 30.0, render_js: bool = True) -> str:
        """Fetch HTML for ``url``, optionally falling back to a JS-rendered snapshot."""

        html = self._fetch_html_requests(url, timeout_s=timeout_s)
        if not render_js:
            return html
        try:
            text = self._preprocessor.html_to_text(html)
        except Exception:
            text = ""
        if self._looks_like_unrendered_shell(text):
            return self._fetch_html_playwright(url, timeout_s=max(timeout_s, 45.0))
        return html


_DEFAULT_FETCHER = HtmlFetcher()


def fetch_html(url: str, *, timeout_s: float = 30.0, render_js: bool = True) -> str:
    """Convenience wrapper around :class:`HtmlFetcher` for callers."""

    return _DEFAULT_FETCHER.fetch_html(url=url, timeout_s=timeout_s, render_js=render_js)
