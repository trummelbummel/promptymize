from __future__ import annotations

import argparse
import sys
from pathlib import Path

from auto_prompt.scraper.config import ScraperConfig, load_config
from auto_prompt.scraper.fetch import HtmlFetcher, fetch_html
from auto_prompt.preprocessing.preprocessing import HtmlPreprocessor, html_to_text
from auto_prompt.scraper.types import WebScrapeResult
from auto_prompt.scraper.writer import ScrapeWriter, write_scrape_outputs


class WebScraper:
    """High-level web scraper orchestrating fetch, preprocess and write steps."""

    def __init__(
        self,
        *,
        fetcher: HtmlFetcher | None = None,
        preprocessor: HtmlPreprocessor | None = None,
        writer: ScrapeWriter | None = None,
    ) -> None:
        self._preprocessor = preprocessor or HtmlPreprocessor()
        self._fetcher = fetcher or HtmlFetcher(preprocessor=self._preprocessor)
        self._writer = writer or ScrapeWriter()

    def write_scrape(
        self,
        *,
        url: str,
        folder_name: str,
        out_root: Path,
        render_js: bool = True,
    ) -> WebScrapeResult:
        """Scrape a single URL into ``out_root``."""

        html = self._fetcher.fetch_html(url=url, render_js=render_js)
        md = self._preprocessor.html_to_markdown(html)
        return self._writer.write(url=url, folder_name=folder_name, html=html, text=md, out_root=out_root)

    def scrape_from_config(
        self,
        config: ScraperConfig,
        *,
        out_root: Path,
        render_js: bool = True,
    ) -> list[WebScrapeResult]:
        """Scrape all targets defined in ``config``, skipping failures."""

        results: list[WebScrapeResult] = []
        for t in config.targets:
            try:
                results.append(
                    self.write_scrape(url=t.url, folder_name=t.folder_name, out_root=out_root, render_js=render_js),
                )
            except Exception as exc:  # noqa: BLE001
                print(f"SKIP {t.url} ({t.folder_name}): {exc}", file=sys.stderr)
        return results


_DEFAULT_SCRAPER = WebScraper()


def write_scrape(*, url: str, folder_name: str, out_root: Path, render_js: bool = True) -> WebScrapeResult:
    """Convenience wrapper around :class:`WebScraper` for callers."""

    return _DEFAULT_SCRAPER.write_scrape(
        url=url,
        folder_name=folder_name,
        out_root=out_root,
        render_js=render_js,
    )


def scrape_from_config(config: ScraperConfig, *, out_root: Path, render_js: bool = True) -> list[WebScrapeResult]:
    """Convenience wrapper around :class:`WebScraper` for callers."""

    return _DEFAULT_SCRAPER.scrape_from_config(config, out_root=out_root, render_js=render_js)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Web scrape to resources/context/<folder_name>/")
    sub = p.add_subparsers(dest="cmd", required=True)

    one = sub.add_parser("one", help="Scrape a single URL")
    one.add_argument("url")
    one.add_argument("folder_name")
    one.add_argument("--out-root", default="resources/context")
    one.add_argument("--no-render-js", action="store_true")

    batch = sub.add_parser("batch", help="Scrape from a YAML config")
    batch.add_argument("config", help="Path to YAML config file")
    batch.add_argument("--out-root", default="resources/context")
    batch.add_argument("--no-render-js", action="store_true")

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    out_root = Path(args.out_root)
    render_js = not args.no_render_js

    if args.cmd == "one":
        result = write_scrape(url=args.url, folder_name=args.folder_name, out_root=out_root, render_js=render_js)
        print(str(result.output_dir))
        return 0

    config = load_config(Path(args.config))
    results = scrape_from_config(config, out_root=out_root, render_js=render_js)
    print("\n".join(str(r.output_dir) for r in results))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

