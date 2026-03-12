from __future__ import annotations

from auto_prompt.scraper.text import html_to_markdown, html_to_text

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


def test_html_to_text_main_only_and_text_only() -> None:
    text = html_to_text(SAMPLE_HTML)
    assert "Nav" not in text
    assert "console.log" not in text
    assert "Title" in text
    assert "Hello" in text


def test_html_to_markdown_re_export() -> None:
    md = html_to_markdown(SAMPLE_HTML)
    assert "Nav" not in md
    assert "console.log" not in md
    assert "Title" in md
    assert "Hello" in md
