import pytest
from convert_html_to_md import convert_html_to_markdown


@pytest.mark.parametrize(
    "html,expected_md",
    [
        # Test <pre> code block conversion (Python)
        (
            "<pre>def foo():\n    return 42\n</pre>",
            "```python\ndef foo():\n    return 42\n```\n",
        ),
        # Test <pre> code block conversion (non-Python)
        ("<pre>echo hello</pre>", "```\necho hello\n```\n"),
        # Test image path update
        (
            '<img src="{{ site.baseurl }}/assets/foo.png" alt="desc">',
            "![desc](/assets/images/foo.png)",
        ),
        # Test <p> to paragraph
        ("<p>Hello world!</p>", "Hello world!\n\n"),
        # Test <a> to Markdown link
        ('<a href="https://example.com">link</a>', "[link](https://example.com)"),
        # Test removal of WordPress comment <p>
        ("<p><!-- /wp:image --></p><p>Keep me</p>", "Keep me\n\n"),
        # Test removal of <p>[latexpage]</p> at top
        ("<p>[latexpage]</p><p>Next</p>", "Next\n\n"),
        # Test heading conversion
        ("<h2>Header</h2>", "## Header\n\n"),
        # Test blockquote conversion
        ("<blockquote>Quote</blockquote>", "> Quote\n\n"),
        # Test unordered list
        ("<ul><li>One</li><li>Two</li></ul>", "- One\n- Two\n\n"),
        # Test ordered list
        ("<ol><li>First</li><li>Second</li></ol>", "1. First\n2. Second\n\n"),
        # Test italics
        ("<i>italic</i> <em>emph</em>", "*italic* *emph*"),
        # Test bold
        ("<strong>bold</strong>", "**bold**"),
        # Test math block
        ("<p>$$x|y$$</p>", "$$x \\mid y$$\n"),
        # Test underlined span as H5
        (
            '<p><span style="text-decoration: underline;">Underlined</span></p>',
            "##### Underlined\n\n",
        ),
        # Test HTML escapes
        ("&lt;tag&gt; &amp; stuff", "<tag> & stuff"),
    ],
)
def test_convert_html_to_markdown(html, expected_md):
    md, unhandled = convert_html_to_markdown(html)
    # Remove leading/trailing whitespace for comparison
    assert md.strip() == expected_md.strip()
    # Should not have unhandled tags for these cases
    assert not unhandled
