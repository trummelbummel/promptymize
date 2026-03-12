from auto_prompt.preprocessing.preprocessing import HtmlPreprocessor, html_to_text


def test_html_preprocessor_and_function_produce_same_output() -> None:
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
    pre = HtmlPreprocessor()
    direct = pre.html_to_text(html)
    via_func = html_to_text(html)

    assert direct == via_func
    assert "Nav" not in direct
    assert "console.log" not in direct
    assert "Title" in direct
    assert "Hello" in direct

