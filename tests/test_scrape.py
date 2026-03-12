from auto_prompt.scraping.scrape import html_to_markdown, resolve_output_dir, sanitize_folder_name


def test_sanitize_folder_name_basic():
    assert sanitize_folder_name("my docs") == "my_docs"
    assert sanitize_folder_name("../oops") == "oops"
    assert sanitize_folder_name("___") == "scrape"


def test_resolve_output_dir_stays_under_root(tmp_path):
    out_root = tmp_path / "resources"
    out_root.mkdir()

    out = resolve_output_dir(out_root=out_root, folder_name="docs")
    assert out.parent == out_root.resolve()


def test_html_to_markdown_extracts_title_and_text():
    html = """
    <html>
      <head><title>Example</title></head>
      <body>
        <nav>nav</nav>
        <main>
          <h1>Hello</h1>
          <pre><code>print("hi")</code></pre>
        </main>
      </body>
    </html>
    """
    title, md = html_to_markdown(html)
    assert title == "Example"
    assert "# Hello" in md
    assert 'print("hi")' in md
