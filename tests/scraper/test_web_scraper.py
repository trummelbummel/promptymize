from pathlib import Path
from typing import List

from auto_prompt.scraper.config import ScraperConfig, ScrapeTarget
from auto_prompt.scraper.types import WebScrapeResult
from auto_prompt.scraper.web_scraper import WebScraper


class DummyFetcher:
    def __init__(self, html: str) -> None:
        self._html = html
        self.called_with: list[str] = []

    def fetch_html(self, url: str, *, timeout_s: float = 30.0, render_js: bool = True) -> str:  # noqa: ARG002
        self.called_with.append(url)
        return self._html


class DummyPreprocessor:
    def __init__(self, text: str) -> None:
        self._text = text
        self.called = 0

    def html_to_markdown(self, html: str) -> str:  # noqa: ARG002
        self.called += 1
        return self._text


class DummyWriter:
    def __init__(self, out_root: Path) -> None:
        self._out_root = out_root
        self.calls: List[WebScrapeResult] = []

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

