import pytest
from convert_html_to_md import (
    a_tags_to_markdown,
    blockquote_to_markdown,
    convert_html_to_markdown,
    heading_tags_to_markdown,
    img_tags_to_markdown,
    italic_tags_to_markdown,
    ordered_lists_to_markdown,
    paragraphs_to_markdown,
    pre_tags_to_markdown,
    remove_doctype_declaration,
    remove_latexpage_br_in_paragraphs,
    remove_latexpage_first_paragraph,
    remove_wp_comment_paragraphs,
    strong_tags_to_markdown,
    strong_underline_span_to_h5_heading,
    underline_span_to_bold,
    underline_span_to_h5_heading,
    unordered_lists_to_markdown,
)
from typing import Tuple, List


@pytest.mark.parametrize(
    "html,expected",
    [
        ("<strong><u>Important</u></strong>", "<h5>Important</h5>"),
        (
            "<strong><u>Text</u></strong> and more",
            "<strong><u>Text</u></strong> and more",
        ),
        ("<p><strong><u>Header</u></strong></p>", "<h5>Header</h5>"),
        ("<p>Normal</p>", "<p>Normal</p>"),
    ],
)
def test_strong_underline_span_to_h5_heading(html, expected):
    assert strong_underline_span_to_h5_heading(html) == expected


@pytest.mark.parametrize(
    "html,expected",
    [
        (
            "<span style='text-decoration: underline;'>Underlined</span>",
            "**Underlined**",
        ),
        (
            "<span style='text-decoration: underline;'>Text</span> and more",
            "**Text** and more",
        ),
        ("<p><span style='text-decoration: underline;'>A</span></p>", "<p>**A**</p>"),
        ("<p>Normal</p>", "<p>Normal</p>"),
    ],
)
def test_underline_span_to_bold(html, expected):
    assert underline_span_to_bold(html) == expected


@pytest.mark.parametrize(
    "html,expected",
    [
        ("<h1>Header 1</h1>", "# Header 1\n\n"),
        ("<h2>Header 2</h2>", "## Header 2\n\n"),
        ("<h3>Header 3</h3>", "### Header 3\n\n"),
        ("<h4>Header 4</h4>", "#### Header 4\n\n"),
        ("<h5>Header 5</h5>", "##### Header 5\n\n"),
        ("<h6>Header 6</h6>", "###### Header 6\n\n"),
    ],
)
def test_heading_tags_to_markdown(html, expected):
    assert heading_tags_to_markdown(html) == expected


@pytest.mark.parametrize(
    "html,expected",
    [
        ("<blockquote>Quote</blockquote>", "> Quote\n\n"),
        ("<blockquote><p>Nested</p></blockquote>", "> Nested\n\n"),
        ("<p>Normal</p>", "<p>Normal</p>"),
    ],
)
def test_blockquote_to_markdown(html, expected):
    assert blockquote_to_markdown(html) == expected


@pytest.mark.parametrize(
    "html,expected",
    [
        ("<i>italic</i>", "*italic*"),
        ("<em>emphasis</em>", "*emphasis*"),
        ("<i>italic</i> and <em>emphasis</em>", "*italic* and *emphasis*"),
        ("<p>Normal</p>", "<p>Normal</p>"),
    ],
)
def test_italic_tags_to_markdown(html, expected):
    assert italic_tags_to_markdown(html) == expected


@pytest.mark.parametrize(
    "html,expected",
    [
        ("<strong>bold</strong>", "**bold**"),
        ("<b>bold</b>", "**bold**"),
        ("<strong>bold</strong> and <b>bold</b>", "**bold** and **bold**"),
        ("<p>Normal</p>", "<p>Normal</p>"),
    ],
)
def test_strong_tags_to_markdown(html, expected):
    assert strong_tags_to_markdown(html) == expected


@pytest.mark.parametrize(
    "html,expected",
    [
        ("<ul><li>Item 1</li><li>Item 2</li></ul>", "- Item 1\n- Item 2\n\n"),
        (
            "<ul><li>Nested<ul><li>Subitem</li></ul></li></ul>",
            "- Nested\n  - Subitem\n\n",
        ),
        ("<p>Normal</p>", "<p>Normal</p>"),
    ],
)
def test_unordered_lists_to_markdown(html, expected):
    assert unordered_lists_to_markdown(html) == expected


@pytest.mark.parametrize(
    "html,expected",
    [
        ("<ol><li>First</li><li>Second</li></ol>", "1. First\n2. Second\n\n"),
        (
            "<ol><li>Nested<ol><li>Subitem</li></ol></li></ol>",
            "1. Nested\n   1. Subitem\n\n",
        ),
        ("<p>Normal</p>", "<p>Normal</p>"),
    ],
)
def test_ordered_lists_to_markdown(html, expected):
    assert ordered_lists_to_markdown(html) == expected


@pytest.mark.parametrize(
    "html,expected",
    [
        ("<pre>Code block</pre>", "```\nCode block\n```\n"),
        ("<pre><code>Indented</code></pre>", "```\nIndented\n```\n"),
        ("<p>Normal</p>", "<p>Normal</p>"),
    ],
)
def test_pre_tags_to_markdown(html, expected):
    assert pre_tags_to_markdown(html) == expected


@pytest.mark.parametrize(
    "html,expected",
    [
        (
            '<img src="/path/to/image.png" alt="Description">',
            "![Description](/path/to/image.png)",
        ),
        ('<img src="/path/to/image.png">', "![](/path/to/image.png)"),
        ("<p>Normal</p>", "<p>Normal</p>"),
    ],
)
def test_img_tags_to_markdown(html, expected):
    assert img_tags_to_markdown(html) == expected


@pytest.mark.parametrize(
    "html,expected",
    [
        ('<a href="https://example.com">Link</a>', "[Link](https://example.com)"),
        ('<a href="https://example.com"></a>', "[](https://example.com)"),
        ("<p>Normal</p>", "<p>Normal</p>"),
    ],
)
def test_a_tags_to_markdown(html, expected):
    assert a_tags_to_markdown(html) == expected


@pytest.mark.parametrize(
    "html,expected",
    [
        ("<p>Paragraph</p>", "Paragraph\n\n"),
        ("<p>Line 1</p><p>Line 2</p>", "Line 1\n\nLine 2\n\n"),
        ("<p>Normal</p>", "Normal\n\n"),
    ],
)
def test_paragraphs_to_markdown(html, expected):
    assert paragraphs_to_markdown(html) == expected


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


@pytest.mark.parametrize(
    "html,expected",
    [
        (
            "<!DOCTYPE html>\n<html><body>Test</body></html>",
            "<html><body>Test</body></html>",
        ),
        (
            "<html><body>No doctype</body></html>",
            "<html><body>No doctype</body></html>",
        ),
        ("<!DOCTYPE html>", ""),
        ("<!DOCTYPE html>\n\n<p>foo</p>", "\n<p>foo</p>"),
    ],
)
def test_remove_doctype_declaration(html, expected):
    assert remove_doctype_declaration(html) == expected


@pytest.mark.parametrize(
    "html,expected",
    [
        ("<p><!-- /wp:image --></p><p>Keep me</p>", "<p>Keep me</p>"),
        ("<p><!-- /wp:paragraph --></p>", ""),
        ("<p>Normal</p>", "<p>Normal</p>"),
        (
            "<p><!-- /wp:image --></p><p><!-- /wp:paragraph --></p><p>Keep</p>",
            "<p>Keep</p>",
        ),
    ],
)
def test_remove_wp_comment_paragraphs(html, expected):
    assert remove_wp_comment_paragraphs(html) == expected


@pytest.mark.parametrize(
    "html,expected",
    [
        ("<p>[latexpage]</p><p>Next</p>", "<p>Next</p>"),
        ("<p>Not latexpage</p><p>Next</p>", "<p>Not latexpage</p><p>Next</p>"),
        ("<p>[latexpage]</p>", ""),
        ("<p>[latexpage]</p><div>Other</div>", "<div>Other</div>"),
    ],
)
def test_remove_latexpage_first_paragraph(html, expected):
    assert remove_latexpage_first_paragraph(html) == expected


@pytest.mark.parametrize(
    "html,expected",
    [
        ("<p>foo<br>[latexpage]</p>", "<p>foo</p>"),
        ("<p>foo<br>bar</p>", "<p>foo<br>bar</p>"),
        ("<p>[latexpage]</p>", "<p>[latexpage]</p>"),
        ("<p>foo<br> [latexpage]</p>", "<p>foo</p>"),
    ],
)
def test_remove_latexpage_br_in_paragraphs(html, expected):
    assert remove_latexpage_br_in_paragraphs(html) == expected


@pytest.mark.parametrize(
    "html,expected",
    [
        (
            '<p><span style="text-decoration: underline;">Underlined</span></p>',
            "<h5>Underlined</h5>",
        ),
        (
            '<p><span style="text-decoration: underline;">Text</span> and more</p>',
            '<p><span style="text-decoration: underline;">Text</span> and more</p>',
        ),
        (
            '<p><span style="text-decoration: underline;">A</span></p><p>B</p>',
            "<h5>A</h5><p>B</p>",
        ),
        (
            "<p>Normal</p>",
            "<p>Normal</p>",
        ),
    ],
)
def test_underline_span_to_h5_heading(html, expected):
    assert underline_span_to_h5_heading(html) == expected
