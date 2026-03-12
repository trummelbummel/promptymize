from __future__ import annotations

import pytest

from auto_prompt.preprocessing.preprocessing import HtmlPreprocessor, html_to_markdown, html_to_text

SAMPLE_HTML = """
<html>
  <body>
    <nav>Nav</nav>
    <main>
      <h1>Title</h1>
      <p>Hello <b>world</b>.</p>
      <script>console.log("no")</script>
    </main>
  </body>
</html>
"""


# -- html_to_text ---------------------------------------------------------


def test_html_to_text_class_and_function_produce_same_output() -> None:
    pre = HtmlPreprocessor()
    direct = pre.html_to_text(SAMPLE_HTML)
    via_func = html_to_text(SAMPLE_HTML)

    assert direct == via_func
    assert "Nav" not in direct
    assert "console.log" not in direct
    assert "Title" in direct
    assert "Hello" in direct


def test_html_to_text_collapses_duplicate_lines() -> None:
    html = "<html><body><main><p>Same</p><p>Same</p><p>Different</p></main></body></html>"
    result = html_to_text(html)
    assert result.count("Same") == 1
    assert "Different" in result


def test_html_to_text_ends_with_newline() -> None:
    html = "<html><body><main><p>Content</p></main></body></html>"
    assert html_to_text(html).endswith("\n")


def test_html_to_text_falls_back_to_article() -> None:
    html = "<html><body><article><p>In article</p></article></body></html>"
    result = html_to_text(html)
    assert "In article" in result


def test_html_to_text_falls_back_to_role_main() -> None:
    html = '<html><body><div role="main"><p>In role main</p></div></body></html>'
    result = html_to_text(html)
    assert "In role main" in result


def test_html_to_text_falls_back_to_body() -> None:
    html = "<html><body><p>In body</p></body></html>"
    result = html_to_text(html)
    assert "In body" in result


def test_html_to_text_strips_all_noise_elements() -> None:
    html = """
    <html><body><main>
      <p>Keep</p>
      <style>.x{}</style>
      <noscript>no</noscript>
      <svg><rect/></svg>
      <header>hdr</header>
      <footer>ftr</footer>
      <nav>nav</nav>
      <aside>aside</aside>
      <form>form</form>
      <div aria-hidden="true">hidden</div>
    </main></body></html>
    """
    result = html_to_text(html)
    assert "Keep" in result
    for noise in ("no", "hdr", "ftr", "nav", "aside", "form", "hidden"):
        assert noise not in result


def test_html_to_text_raises_when_no_container() -> None:
    html = "<html></html>"
    with pytest.raises(ValueError, match="Could not find"):
        html_to_text(html)


# -- html_to_markdown -----------------------------------------------------


def test_html_to_markdown_class_and_function_produce_same_output() -> None:
    pre = HtmlPreprocessor()
    md_direct = pre.html_to_markdown(SAMPLE_HTML)
    md_func = html_to_markdown(SAMPLE_HTML)

    assert md_direct == md_func
    assert "Nav" not in md_direct
    assert "console.log" not in md_direct
    assert "Title" in md_direct
    assert "Hello" in md_direct


def test_html_to_markdown_contains_atx_heading() -> None:
    html = "<html><body><main><h2>Section</h2><p>Text</p></main></body></html>"
    md = html_to_markdown(html)
    assert md.startswith("## Section")


def test_html_to_markdown_ends_with_newline() -> None:
    html = "<html><body><main><p>Content</p></main></body></html>"
    assert html_to_markdown(html).endswith("\n")


# -- split_on_headers -----------------------------------------------------


def test_split_on_headers_basic() -> None:
    md = "# H1\nParagraph\n## H2\nMore text"
    sections = HtmlPreprocessor.split_on_headers(md)
    assert len(sections) == 2
    assert sections[0].startswith("# H1")
    assert sections[1].startswith("## H2")


def test_split_on_headers_no_headers() -> None:
    md = "Just plain text\nwith no headers."
    sections = HtmlPreprocessor.split_on_headers(md)
    assert len(sections) == 1
    assert "Just plain text" in sections[0]


def test_split_on_headers_empty_input() -> None:
    assert HtmlPreprocessor.split_on_headers("") == []
    assert HtmlPreprocessor.split_on_headers("   ") == []


def test_split_on_headers_multiple_levels() -> None:
    md = "# H1\nA\n## H2\nB\n### H3\nC\n#### H4\nD"
    sections = HtmlPreprocessor.split_on_headers(md)
    assert len(sections) == 4


def test_split_on_headers_preserves_content_under_header() -> None:
    md = "## Overview\n- bullet 1\n- bullet 2\n## Details\nParagraph."
    sections = HtmlPreprocessor.split_on_headers(md)
    assert "bullet 1" in sections[0]
    assert "Paragraph" in sections[1]


def test_split_on_headers_preamble_before_first_header() -> None:
    md = "Some preamble text.\n# First header\nBody."
    sections = HtmlPreprocessor.split_on_headers(md)
    assert len(sections) == 2
    assert "preamble" in sections[0]
    assert sections[1].startswith("# First header")
