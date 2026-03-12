from __future__ import annotations

from unittest.mock import MagicMock, patch

from auto_prompt.scraper.fetch import HtmlFetcher


# -- _looks_like_unrendered_shell ------------------------------------------


def test_looks_like_shell_loading_text() -> None:
    fetcher = HtmlFetcher()
    assert fetcher._looks_like_unrendered_shell("Loading...\n") is True


def test_looks_like_shell_short_content() -> None:
    fetcher = HtmlFetcher()
    assert fetcher._looks_like_unrendered_shell("Hi") is True


def test_looks_like_shell_real_content() -> None:
    fetcher = HtmlFetcher()
    long_text = "A real paragraph. " * 50
    assert fetcher._looks_like_unrendered_shell(long_text) is False


def test_looks_like_shell_many_lines_with_loading() -> None:
    fetcher = HtmlFetcher()
    text = "\n".join(["line"] * 5 + ["Loading..."])
    assert fetcher._looks_like_unrendered_shell(text) is True


def test_looks_like_shell_many_lines_without_loading() -> None:
    """Over 30 non-empty lines without 'Loading...' and >400 chars should be False."""
    fetcher = HtmlFetcher()
    text = "\n".join([f"Line number {i} with enough text to be long" for i in range(40)])
    assert fetcher._looks_like_unrendered_shell(text) is False


# -- fetch_html with render_js=False (no fallback) -------------------------


@patch("auto_prompt.scraper.fetch.requests.get")
def test_fetch_html_no_js_returns_requests_response(mock_get: MagicMock) -> None:
    mock_resp = MagicMock()
    mock_resp.text = "<html><body><main>Content</main></body></html>"
    mock_resp.encoding = "utf-8"
    mock_get.return_value = mock_resp

    fetcher = HtmlFetcher()
    result = fetcher.fetch_html("https://example.com", render_js=False)

    assert result == mock_resp.text
    mock_resp.raise_for_status.assert_called_once()


# -- fetch_html with render_js=True, content is substantial ----------------


@patch("auto_prompt.scraper.fetch.requests.get")
def test_fetch_html_with_js_skips_playwright_when_content_is_substantial(mock_get: MagicMock) -> None:
    html = "<html><body><main><p>" + "Real content. " * 50 + "</p></main></body></html>"
    mock_resp = MagicMock()
    mock_resp.text = html
    mock_resp.encoding = "utf-8"
    mock_get.return_value = mock_resp

    fetcher = HtmlFetcher()
    result = fetcher.fetch_html("https://example.com", render_js=True)

    assert result == html


# -- fetch_html with render_js=True, content is thin (falls back) ---------


@patch("auto_prompt.scraper.fetch.requests.get")
def test_fetch_html_falls_back_to_playwright_for_thin_content(mock_get: MagicMock) -> None:
    mock_resp = MagicMock()
    mock_resp.text = "<html><body><main>Loading...</main></body></html>"
    mock_resp.encoding = "utf-8"
    mock_get.return_value = mock_resp

    fetcher = HtmlFetcher()
    with patch.object(fetcher, "_fetch_via_playwright", return_value="<html>Rendered</html>") as mock_pw:
        result = fetcher.fetch_html("https://example.com", render_js=True)

    assert result == "<html>Rendered</html>"
    mock_pw.assert_called_once()
