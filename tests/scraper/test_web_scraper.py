from __future__ import annotations

from pathlib import Path

from auto_prompt.scraper.config import ScraperConfig, ScrapeTarget
from auto_prompt.scraper.types import WebScrapeResult
from auto_prompt.scraper.web_scraper import WebScraper, build_parser


# -- Stubs -----------------------------------------------------------------


class DummyFetcher:
    """Stub fetcher that returns a fixed HTML string."""

    def __init__(self, html: str) -> None:
        self._html = html
        self.called_with: list[str] = []

    def fetch_html(self, url: str, *, timeout_s: float = 30.0, render_js: bool = True) -> str:  # noqa: ARG002
        self.called_with.append(url)
        return self._html


class FailingFetcher:
    """Stub fetcher that always raises."""

    def fetch_html(self, url: str, *, timeout_s: float = 30.0, render_js: bool = True) -> str:  # noqa: ARG002
        msg = "connection refused"
        raise ConnectionError(msg)


class DummyPreprocessor:
    """Stub preprocessor that returns a fixed Markdown string."""

    def __init__(self, text: str) -> None:
        self._text = text
        self.called = 0

    def html_to_markdown(self, html: str) -> str:  # noqa: ARG002
        self.called += 1
        return self._text


class DummyWriter:
    """Stub writer that writes minimal files and records calls."""

    def __init__(self, out_root: Path) -> None:
        self._out_root = out_root
        self.calls: list[WebScrapeResult] = []

    def write(self, *, url: str, folder_name: str, html: str, text: str, out_root: Path) -> WebScrapeResult:  # noqa: ARG002
        output_dir = self._out_root / folder_name
        output_dir.mkdir(parents=True, exist_ok=True)
        markdown_path = output_dir / "page.md"
        html_path = output_dir / "source.html"
        meta_path = output_dir / "meta.json"
        markdown_path.write_text(text, encoding="utf-8")
        html_path.write_text(html, encoding="utf-8")
        meta_path.write_text("{}", encoding="utf-8")

        result = WebScrapeResult(
            url=url,
            folder_name=folder_name,
            output_dir=output_dir,
            markdown_path=markdown_path,
            html_path=html_path,
            meta_path=meta_path,
        )
        self.calls.append(result)
        return result


# -- WebScraper.write_scrape -----------------------------------------------


def test_web_scraper_write_scrape_uses_collaborators(tmp_path: Path) -> None:
    dummy_fetcher = DummyFetcher("<html><body><main><p>Hello</p></main></body></html>")
    dummy_pre = DummyPreprocessor("Hello\n")
    dummy_writer = DummyWriter(tmp_path / "resources")

    scraper = WebScraper(fetcher=dummy_fetcher, preprocessor=dummy_pre, writer=dummy_writer)

    out_root = tmp_path / "resources"
    result = scraper.write_scrape(
        url="https://example.com",
        folder_name="docs",
        out_root=out_root,
        render_js=False,
    )

    assert dummy_fetcher.called_with == ["https://example.com"]
    assert dummy_pre.called == 1
    assert result.output_dir.exists()
    assert result.markdown_path.read_text(encoding="utf-8") == "Hello\n"


# -- WebScraper.scrape_from_config -----------------------------------------


def test_web_scraper_scrape_from_config_multiple_targets(tmp_path: Path) -> None:
    dummy_fetcher = DummyFetcher("<html><body><main><p>Hello</p></main></body></html>")
    dummy_pre = DummyPreprocessor("Hello\n")
    dummy_writer = DummyWriter(tmp_path / "resources")

    scraper = WebScraper(fetcher=dummy_fetcher, preprocessor=dummy_pre, writer=dummy_writer)

    cfg = ScraperConfig(
        targets=[
            ScrapeTarget(folder_name="docs1", url="https://example.com/a"),
            ScrapeTarget(folder_name="docs2", url="https://example.com/b"),
        ],
    )
    out_root = tmp_path / "resources"
    results = scraper.scrape_from_config(cfg, out_root=out_root, render_js=False)

    assert [r.folder_name for r in results] == ["docs1", "docs2"]
    assert dummy_fetcher.called_with == ["https://example.com/a", "https://example.com/b"]
    assert dummy_pre.called == 2


def test_scrape_from_config_skips_failures(tmp_path: Path) -> None:
    dummy_pre = DummyPreprocessor("ignored")
    dummy_writer = DummyWriter(tmp_path / "resources")

    scraper = WebScraper(fetcher=FailingFetcher(), preprocessor=dummy_pre, writer=dummy_writer)

    cfg = ScraperConfig(
        targets=[
            ScrapeTarget(folder_name="fail", url="https://bad.example.com"),
        ],
    )
    results = scraper.scrape_from_config(cfg, out_root=tmp_path / "resources", render_js=False)
    assert results == []


def test_scrape_from_config_continues_after_failure(tmp_path: Path) -> None:
    """If the first target fails, subsequent targets should still be scraped."""

    class AlternatingFetcher:
        def __init__(self) -> None:
            self._call = 0

        def fetch_html(self, url: str, *, timeout_s: float = 30.0, render_js: bool = True) -> str:  # noqa: ARG002
            self._call += 1
            if self._call == 1:
                raise ConnectionError("boom")
            return "<html><body><main><p>OK</p></main></body></html>"

    dummy_pre = DummyPreprocessor("OK\n")
    dummy_writer = DummyWriter(tmp_path / "resources")
    scraper = WebScraper(fetcher=AlternatingFetcher(), preprocessor=dummy_pre, writer=dummy_writer)

    cfg = ScraperConfig(
        targets=[
            ScrapeTarget(folder_name="first", url="https://example.com/a"),
            ScrapeTarget(folder_name="second", url="https://example.com/b"),
        ],
    )
    results = scraper.scrape_from_config(cfg, out_root=tmp_path / "resources", render_js=False)
    assert len(results) == 1
    assert results[0].folder_name == "second"


# -- build_parser ----------------------------------------------------------


def test_build_parser_one_subcommand() -> None:
    parser = build_parser()
    args = parser.parse_args(["one", "https://example.com", "docs", "--out-root", "/tmp/out"])
    assert args.cmd == "one"
    assert args.url == "https://example.com"
    assert args.folder_name == "docs"
    assert args.out_root == "/tmp/out"
    assert args.no_render_js is False


def test_build_parser_batch_subcommand() -> None:
    parser = build_parser()
    args = parser.parse_args(["batch", "config.yaml", "--no-render-js"])
    assert args.cmd == "batch"
    assert args.config == "config.yaml"
    assert args.no_render_js is True


def test_build_parser_one_defaults() -> None:
    parser = build_parser()
    args = parser.parse_args(["one", "https://example.com", "docs"])
    assert args.out_root == "resources/context"
    assert args.no_render_js is False
