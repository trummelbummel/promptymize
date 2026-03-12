from scraper.text import html_to_text


def test_html_to_text_main_only_and_text_only() -> None:
    html = """
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
    text = html_to_text(html)
    assert "Nav" not in text
    assert "console.log" not in text
    assert "Title" in text
    assert "Hello" in text

