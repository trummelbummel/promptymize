from __future__ import annotations

import json
from pathlib import Path

from auto_prompt.scraper.writer import ScrapeWriter, write_scrape_outputs


def _write_kwargs(out_root: Path) -> dict:
    return dict(
        url="https://example.com/page",
        folder_name="docs",
        html="<html><body><main><p>Hello</p></main></body></html>",
        text="Hello\n",
        out_root=out_root,
    )


# -- ScrapeWriter.write / write_scrape_outputs consistency -----------------


def test_scrape_writer_and_function_write_same_structure(tmp_path: Path) -> None:
    writer = ScrapeWriter()
    out_root = tmp_path / "resources"
    out_root.mkdir()

    kwargs = _write_kwargs(out_root)
    result_class = writer.write(**kwargs)
    result_func = write_scrape_outputs(**kwargs)

    assert result_class.output_dir == result_func.output_dir
    assert result_class.markdown_path.read_text(encoding="utf-8") == "Hello\n"
    assert result_class.html_path.read_text(encoding="utf-8").strip() != ""
    assert result_class.meta_path.read_text(encoding="utf-8").strip() != ""


# -- Written file contents ------------------------------------------------


def test_writer_creates_all_three_files(tmp_path: Path) -> None:
    out_root = tmp_path / "resources"
    out_root.mkdir()
    result = ScrapeWriter().write(**_write_kwargs(out_root))

    assert result.markdown_path.exists()
    assert result.html_path.exists()
    assert result.meta_path.exists()


def test_writer_markdown_matches_text_input(tmp_path: Path) -> None:
    out_root = tmp_path / "resources"
    out_root.mkdir()
    result = ScrapeWriter().write(**_write_kwargs(out_root))
    assert result.markdown_path.read_text(encoding="utf-8") == "Hello\n"


def test_writer_html_matches_html_input(tmp_path: Path) -> None:
    out_root = tmp_path / "resources"
    out_root.mkdir()
    kwargs = _write_kwargs(out_root)
    result = ScrapeWriter().write(**kwargs)
    assert result.html_path.read_text(encoding="utf-8") == kwargs["html"]


def test_writer_meta_json_has_expected_keys(tmp_path: Path) -> None:
    out_root = tmp_path / "resources"
    out_root.mkdir()
    result = ScrapeWriter().write(**_write_kwargs(out_root))
    meta = json.loads(result.meta_path.read_text(encoding="utf-8"))

    assert meta["url"] == "https://example.com/page"
    assert meta["folder_name"] == "docs"
    assert meta["hostname"] == "example.com"
    assert "scraped_at" in meta
    assert "markdown" in meta["output"]
    assert "html" in meta["output"]


def test_writer_result_paths_are_inside_output_dir(tmp_path: Path) -> None:
    out_root = tmp_path / "resources"
    out_root.mkdir()
    result = ScrapeWriter().write(**_write_kwargs(out_root))

    assert result.markdown_path.parent == result.output_dir
    assert result.html_path.parent == result.output_dir
    assert result.meta_path.parent == result.output_dir
