import pytest
from convert_html_to_md import convert_html_to_markdown
from typing import Tuple, List
from convert_html_to_md import (
    remove_doctype_declaration,
    remove_wp_comment_paragraphs,
    remove_latexpage_first_paragraph,
    remove_latexpage_br_in_paragraphs,
    underline_span_to_h5_heading,
    strong_underline_span_to_h5_heading,
    underline_span_to_bold,
    heading_tags_to_markdown,
    blockquote_to_markdown,
    italic_tags_to_markdown,
    strong_tags_to_markdown,
    unordered_lists_to_markdown,
    ordered_lists_to_markdown,
    pre_tags_to_markdown,
    img_tags_to_markdown,
    a_tags_to_markdown,
    paragraphs_to_markdown,
)


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
