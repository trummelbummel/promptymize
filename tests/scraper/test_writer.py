from pathlib import Path

from auto_prompt.scraper.writer import ScrapeWriter, write_scrape_outputs


def test_scrape_writer_and_function_write_same_structure(tmp_path: Path) -> None:
    writer = ScrapeWriter()
    out_root = tmp_path / "resources"
    out_root.mkdir()

    kwargs = dict(
        url="https://example.com",
        folder_name="docs",
        html="<html><body><main><p>Hello</p></main></body></html>",
        text="Hello\n",
        out_root=out_root,
    )

    result_class = writer.write(**kwargs)
    result_func = write_scrape_outputs(**kwargs)

    # Both should write into the same directory layout.
    assert result_class.output_dir == result_func.output_dir
    assert result_class.markdown_path.read_text(encoding="utf-8") == "Hello\n"
    assert result_class.html_path.read_text(encoding="utf-8").strip() != ""
    assert result_class.meta_path.read_text(encoding="utf-8").strip() != ""

