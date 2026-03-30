from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests
import yaml
from bs4 import BeautifulSoup
from markdownify import markdownify as html_to_md

from auto_prompt.errors import ConfigurationError, DependencyUnavailableError
from auto_prompt.preprocessing.preprocessing import HtmlPreprocessor
from auto_prompt.scraper.paths import resolve_output_dir


@dataclass(frozen=True)
class ScrapeTarget:
    folder_name: str
    urls: list[str]


def _extracted_md_is_loading_only(md: str) -> bool:
    """
    Heuristic: after conversion, some pages end up with nothing but "Loading..."
    placeholders (often from JS apps that didn't fully render).
    """

    lines = [ln.strip() for ln in md.splitlines() if ln.strip()]
    if not lines:
        return True

    # Consider only "Loading..." and a couple of common variants as noise.
    noise = {"loading...", "loading..", "loading"}
    meaningful = [ln for ln in lines if ln.lower() not in noise]
    return not meaningful


def _project_root() -> Path:
    # src/auto_prompt/scraper/web_scraper.py -> src/auto_prompt/scraper -> auto_prompt -> src -> project root
    return Path(__file__).resolve().parents[3]


def _load_targets_from_yaml(path: Path) -> list[ScrapeTarget]:
    if not path.exists():
        raise ConfigurationError(f"Scraper config not found: {path}")

    data: Any = yaml.safe_load(path.read_text(encoding="utf-8"))
    targets_raw = (data or {}).get("targets")
    if not isinstance(targets_raw, list):
        raise ConfigurationError("Invalid scraper YAML: expected top-level 'targets' list")

    targets: list[ScrapeTarget] = []
    for entry in targets_raw:
        if not isinstance(entry, dict):
            raise ConfigurationError("Invalid scraper YAML: each target must be a mapping")
        folder_name = entry.get("folder_name")
        urls = entry.get("url")
        if not isinstance(folder_name, str) or not folder_name.strip():
            raise ConfigurationError("Invalid scraper YAML: missing/blank 'folder_name'")
        if not isinstance(urls, list) or not all(isinstance(u, str) and u.strip() for u in urls):
            raise ConfigurationError(f"Invalid scraper YAML: missing/invalid 'url' list for {folder_name!r}")
        targets.append(ScrapeTarget(folder_name=folder_name, urls=[u.strip() for u in urls]))
    return targets


def _fetch_html(*, url: str, timeout_seconds: float) -> str:
    headers = {
        "User-Agent": "promptymize/1.0 (+https://github.com/trummelbummel/promptymize)",
    }
    try:
        resp = requests.get(url, headers=headers, timeout=timeout_seconds)
        resp.raise_for_status()
        html = resp.text
        if _looks_unrendered(html):
            return _fetch_html_with_playwright(url=url, timeout_seconds=timeout_seconds)
        return html
    except requests.exceptions.RequestException as exc:
        raise DependencyUnavailableError(f"Fetch failed for {url!r}: {exc}") from exc


def _looks_unrendered(html: str) -> bool:
    """
    Heuristic for "JS app still loading" shells.

    Many docs SPAs show some form of "Loading..." plus guidance to enable JavaScript.
    """

    normalized = html.lower()
    return ("loading..." in normalized or "loading" in normalized) and (
        "enable javascript" in normalized or "please enable javascript" in normalized or "<noscript" in normalized
    )


def _fetch_html_with_playwright(*, url: str, timeout_seconds: float) -> str:
    try:
        from playwright.sync_api import sync_playwright
    except Exception as exc:  # pragma: no cover
        raise DependencyUnavailableError("Playwright is not available; cannot render dynamic pages.") from exc

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # Try a couple of different "wait" strategies because docs SPAs can be
            # either network-idle or load-idle depending on client-side fetching.
            attempts = [
                ("networkidle", 750),
                ("load", 3000),
            ]
            last_html = ""
            for wait_until, settle_ms in attempts:
                page.goto(url, wait_until=wait_until, timeout=timeout_seconds * 1000)
                page.wait_for_timeout(settle_ms)
                last_html = page.content()
                if not _looks_unrendered(last_html):
                    browser.close()
                    return last_html

            browser.close()
            raise DependencyUnavailableError("Page still appears unrendered after Playwright render.")
    except Exception as exc:
        raise DependencyUnavailableError(f"Playwright render failed for {url!r}: {exc}") from exc


def _html_to_markdown(html: str) -> str:
    """
    Convert HTML into Markdown.

    Prefers the repo's HtmlPreprocessor (which extracts a main container) and
    falls back to converting the full body if the preprocessor can't locate a
    suitable container.
    """

    try:
        return HtmlPreprocessor().html_to_markdown(html)
    except Exception:
        soup = BeautifulSoup(html, "html.parser")
        body = soup.body or soup
        md = html_to_md(str(body), heading_style="ATX", code_language_callback=lambda _: "")
        md = md.replace("\r\n", "\n").strip()
        return md


def _append_url_markdown(*, page_md_path: Path, url: str, md: str, first: bool) -> None:
    page_md_path.parent.mkdir(parents=True, exist_ok=True)
    with page_md_path.open("a" if not first else "w", encoding="utf-8") as f:
        if not first:
            f.write("\n\n---\n\n")
        f.write(f"## Source\n{url}\n\n")
        f.write(md.strip())
        if not md.endswith("\n"):
            f.write("\n")


def _run_batch(
    *,
    config_path: Path,
    out_root: Path,
    timeout_seconds: float,
    max_targets: int | None,
    max_urls: int | None,
) -> int:
    targets = _load_targets_from_yaml(config_path)
    if max_targets is not None:
        targets = targets[:max_targets]

    any_failed = False
    urls_seen = 0
    for target in targets:
        out_dir = resolve_output_dir(out_root=out_root, folder_name=target.folder_name)
        page_md_path = out_dir / "page.md"

        first = True
        out_dir.mkdir(parents=True, exist_ok=True)
        if page_md_path.exists():
            page_md_path.unlink()

        for url in target.urls:
            if max_urls is not None and urls_seen >= max_urls:
                break
            urls_seen += 1
            try:
                html = _fetch_html(url=url, timeout_seconds=timeout_seconds)
                md = _html_to_markdown(html)
                if _extracted_md_is_loading_only(md):
                    raise DependencyUnavailableError("Extracted content looks like a JS loading shell.")
                _append_url_markdown(
                    page_md_path=page_md_path,
                    url=url,
                    md=md,
                    first=first,
                )
                first = False
            except DependencyUnavailableError as exc:
                any_failed = True
                print(f"[scraper] Failed URL: {url}. Error: {exc}", file=sys.stderr)

        # If no URLs succeeded for a folder, keep it empty; callers may decide how to handle.

    return 1 if any_failed else 0


def _run_one(
    *,
    url: str,
    folder_name: str,
    out_root: Path,
    timeout_seconds: float,
) -> int:
    out_dir = resolve_output_dir(out_root=out_root, folder_name=folder_name)
    page_md_path = out_dir / "page.md"
    html = _fetch_html(url=url, timeout_seconds=timeout_seconds)
    md = _html_to_markdown(html)
    if _extracted_md_is_loading_only(md):
        raise DependencyUnavailableError("Extracted content looks like a JS loading shell.")
    _append_url_markdown(page_md_path=page_md_path, url=url, md=md, first=True)
    return 0


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="promptymize-web-scrape")
    sub = parser.add_subparsers(dest="mode", required=True)

    one = sub.add_parser("one", help="Scrape a single URL into one folder's page.md")
    one.add_argument("url", type=str)
    one.add_argument("folder_name", type=str)
    one.add_argument("--out-root", type=Path, default=None)
    one.add_argument("--timeout-seconds", type=float, default=20.0)

    batch = sub.add_parser("batch", help="Scrape multiple targets from scraper_targets.yaml")
    batch.add_argument("config_path", type=Path)
    batch.add_argument("--out-root", type=Path, default=None)
    batch.add_argument("--timeout-seconds", type=float, default=20.0)
    batch.add_argument("--max-targets", type=int, default=None)
    batch.add_argument("--max-urls", type=int, default=None)

    args = parser.parse_args(argv)
    out_root = args.out_root or (_project_root() / "sources" / "data")

    if args.mode == "one":
        rc = _run_one(
            url=args.url,
            folder_name=args.folder_name,
            out_root=out_root,
            timeout_seconds=args.timeout_seconds,
        )
    else:
        rc = _run_batch(
            config_path=args.config_path,
            out_root=out_root,
            timeout_seconds=args.timeout_seconds,
            max_targets=args.max_targets,
            max_urls=args.max_urls,
        )
    raise SystemExit(rc)

