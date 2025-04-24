#!/usr/bin/env python3
"""
convert_html_to_md.py

A script to convert old HTML files from your website into Markdown files
suitable for a new Jekyll site.

Features:
- Strips the front matter except for: layout, title, date, header-img.
- Sets the layout field in the front matter to "post" for all posts.
- Converts HTML <pre> code blocks to Markdown fenced code blocks (with Python syntax highlighting when appropriate).
- Updates image paths from "{{ site.baseurl }}/assets/..." to "/assets/images/..."
- Converts <p>...</p> blocks into paragraphs, preserving inline spacing to avoid extra spaces before punctuation.
- Converts hyperlinks (<a> tags) to Markdown link syntax.
- Removes entire <p> elements that contain WordPress-style comments (e.g., <!-- /wp:image -->).
- Removes a <p>[latexpage]</p> at the very top of any post.
- Converts heading tags (<h2>–<h6>) to their appropriate Markdown header syntax.
- Converts <blockquote> blocks to Markdown blockquotes.
- Converts unordered lists (<ul> with <li>) to Markdown bullet lists.
- Converts ordered lists (<ol> with <li>) to Markdown numbered lists.
- Replaces HTML italic tags (<i> and <em>) with Markdown italics.
- Converts HTML <strong> tags to Markdown bold.
- Detects isolated math equations in <p> tags and converts them so that:
    - any existing math dollar signs are removed,
    - leading/trailing whitespace is trimmed,
    - any vertical bar characters ("|") are replaced with " \\mid " (with spaces),
    - and the equation is wrapped in a single pair of dollar signs on its own line.
- Replaces underlined text created with <p><span style="text-decoration: underline;">...</span></p>
  with a Markdown level-5 heading (i.e., starting with "#####").
- Replaces HTML escape sequences: &lt; with <, &gt; with >, and &amp; with &.
- Processes one file or all HTML files in a directory.
- Optionally copies images referenced in the Markdown from a source image directory to a target image directory.
  If an image is not found in the source directory, a warning is printed.
- Prints a warning (once per file) if any HTML tags are not explicitly handled.

Dependencies:
- BeautifulSoup4 (bs4)
- PyYAML
- argparse
- pathlib
"""

import argparse
import os
import re
import sys
import shutil
from pathlib import Path
from typing import Optional, Tuple, Set

import yaml
from bs4 import BeautifulSoup, NavigableString, Comment

# Define Python keywords for code detection.
PYTHON_KEYWORDS = ["def ", "import ", "class ", "print(", "in range("]


def print_warning(msg: str) -> None:
    print(f"\033[93m{msg} \033[0m")


def print_error(msg: str) -> None:
    print(f"\033[91m{msg} \033[0m")


def is_math_expression(text: str) -> bool:
    """
    Determine whether the given text appears to be a LaTeX/MathJax math expression.
    We consider it math if it starts and ends with a '$'.
    """
    if text.startswith("$") and text.endswith("$"):
        return True
    return False


def parse_front_matter(text: str) -> Tuple[dict, str]:
    """
    Extract YAML front matter from text if present.
    Returns a tuple: (front_matter_dict, content_without_front_matter)
    """
    fm_pattern = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
    match = fm_pattern.match(text)
    front_matter = {}
    if match:
        fm_text = match.group(1)
        try:
            data = yaml.safe_load(fm_text)
        except yaml.YAMLError as e:
            print_error(f"\nError parsing YAML front matter: {e}")
            data = {}
        # Keep only the desired fields.
        keys_to_keep = ["layout", "title", "date", "header-img"]
        front_matter = {k: v for k, v in data.items() if k in keys_to_keep}
        # Force the layout to always be "post"
        front_matter["layout"] = "post"
        text = text[match.end() :]
    return front_matter, text


def update_image_src(src: str) -> str:
    """
    Update the image source from the old template path to the new /assets/images/ folder.
    Example: '{{ site.baseurl }}/assets/special_9x9_ss.png' becomes '/assets/images/special_9x9_ss.png'
    """
    new_src = re.sub(r"\{\{\s*site\.baseurl\s*\}\}/assets/", "/assets/images/", src)
    return new_src


def is_probably_python(code_text: str) -> bool:
    """
    A heuristic to decide if the code in a <pre> block is Python.
    Checks for common Python keywords.
    """
    return any(kw in code_text for kw in PYTHON_KEYWORDS)


def convert_html_to_markdown(html_text: str) -> Tuple[str, Set[str]]:
    """
    Convert the HTML content into Markdown.
    Also prints a warning (once per file) for any unhandled HTML tags.
    Returns a tuple of the Markdown text and a set of unhandled tag names.
    """
    soup = BeautifulSoup(html_text, "html.parser")

    # Remove entire <p> tags that contain WordPress-style comments.
    for comment in soup.find_all(string=lambda t: isinstance(t, Comment)):
        if "wp:" in comment:
            if comment.parent and comment.parent.name == "p":
                comment.parent.decompose()

    # Remove <p>[latexpage]</p> if it is the very first paragraph.
    first_p = soup.find("p")
    if first_p and first_p.get_text(strip=True) == "[latexpage]":
        first_p.decompose()

    # Remove [latexpage]<br /> at the very beginning of a <p> tag and keep the rest
    for p in soup.find_all("p"):
        if p.contents and isinstance(p.contents[0], NavigableString):
            if "[latexpage]" in p.contents[0]:
                p.contents[0].replace_with(p.contents[0].replace("[latexpage]", ""))
        for br in p.find_all("br"):
            br.extract()

    # Convert underlined text created with <p><span style="text-decoration: underline;">...</span></p>
    # to Markdown H5 headings.
    for p in soup.find_all("p"):
        children = list(p.children)
        if len(children) == 1 and children[0].name == "span":
            span = children[0]
            if span.has_attr("style") and "text-decoration: underline" in span["style"]:
                heading_text = span.get_text(strip=True)
                md_heading = f"##### {heading_text}\n\n"
                p.replace_with(NavigableString(md_heading))

    # Convert any <span style="text-decoration: underline;">...</span> to Markdown bold
    for span in soup.find_all("span"):
        if span.has_attr("style") and "text-decoration: underline" in span["style"]:
            bold_text = f"**{span.get_text(strip=True)}**"
            span.replace_with(NavigableString(bold_text))

    # Convert heading tags (<h2> to <h6>) to Markdown header syntax.
    for level in range(2, 7):
        for header in soup.find_all(f"h{level}"):
            header_text = header.get_text(separator=" ", strip=True)
            md_header = f"{'#' * level} {header_text}\n\n"
            header.replace_with(NavigableString(md_header))

    # Convert <blockquote> tags.
    for blockquote in soup.find_all("blockquote"):
        blockquote_text = blockquote.get_text(separator="\n", strip=True)
        lines = blockquote_text.splitlines()
        md_blockquote = "\n".join(["> " + line for line in lines]) + "\n\n"
        blockquote.replace_with(NavigableString(md_blockquote))

    # Convert unordered lists (<ul> with <li>) to Markdown bullet lists.
    for ul in list(soup.find_all("ul")):
        items = []
        for li in ul.find_all("li", recursive=False):
            li_text = li.get_text(separator=" ", strip=True)
            items.append(f"- {li_text}")
        md_ul = "\n".join(items) + "\n\n"
        ul.replace_with(NavigableString(md_ul))

    # Convert ordered lists (<ol> with <li>) to Markdown numbered lists.
    for ol in list(soup.find_all("ol")):
        items = []
        for idx, li in enumerate(ol.find_all("li", recursive=False), start=1):
            li_text = li.get_text(separator=" ", strip=True)
            items.append(f"{idx}. {li_text}")
        md_ol = "\n".join(items) + "\n\n"
        ol.replace_with(NavigableString(md_ol))

    # Convert italic tags (<i> and <em>) to Markdown italics.
    for tag in list(soup.find_all(["i", "em"])):
        italic_text = tag.get_text()
        md_italic = f"*{italic_text}*"
        tag.replace_with(NavigableString(md_italic))

    # Convert <strong> tags to Markdown bold.
    for tag in list(soup.find_all("strong")):
        strong_text = tag.get_text()
        md_strong = f"**{strong_text}**"
        tag.replace_with(NavigableString(md_strong))

    # Convert <pre> tags (code blocks).
    for pre in soup.find_all("pre"):
        code_text = pre.get_text()  # preserves whitespace and indentation
        language = "python" if is_probably_python(code_text) else ""
        code_text = code_text.strip("\n")
        md_code = f"```{language}\n{code_text}\n```\n"
        pre.replace_with(NavigableString(md_code))

    # Convert <img> tags to Markdown image syntax.
    for img in soup.find_all("img"):
        src = img.get("src", "")
        new_src = update_image_src(src)
        alt = img.get("alt", "")
        md_img = f"![{alt}]({new_src})"
        img.replace_with(NavigableString(md_img))

    # Convert <a> tags to Markdown hyperlink syntax.
    for a in soup.find_all("a"):
        href = a.get("href", "")
        link_text = a.text
        md_link = f"[{link_text}]({href})"
        a.replace_with(NavigableString(md_link))

    # Convert <p> tags.
    # For each paragraph, if it appears to be an isolated math expression,
    # remove any existing $ symbols, trim whitespace, replace vertical bar symbols with " \\mid ",
    # then re-wrap in $...$ on its own line.
    # Otherwise, convert the paragraph normally.
    for p in soup.find_all("p"):
        text = p.get_text(strip=True)
        if is_math_expression(text):
            eq = text.strip("$").strip()
            eq = eq.replace(
                "|", " \\mid "
            )  # Replace vertical bar with " \mid " (with spaces)
            eq = eq.replace("\\mathrm{log}", "\\log ")  # Replace \mathrm{log} with \log
            new_text = f"${eq}$\n"
        else:
            new_text = "".join(str(child) for child in p.contents).strip() + "\n\n"
        p.replace_with(NavigableString(new_text))

    # Check for any remaining (unhandled) HTML tags (excluding common inline tags like <br>).
    unhandled_tags = {tag.name for tag in soup.find_all() if tag.name not in ["br"]}
    if unhandled_tags:
        print_warning(
            f"\n\tWarning: The following HTML tags were not explicitly handled: {', '.join(unhandled_tags)}"
        )

    # Remove any remaining HTML tags.
    intermediate = str(soup)
    markdown_text = re.sub(r"<[^>]+>", "", intermediate)
    markdown_text = re.sub(r"\n{3,}", "\n\n", markdown_text)

    # Replace HTML entities with their literal characters.
    markdown_text = markdown_text.replace("&lt;", "<")
    markdown_text = markdown_text.replace("&gt;", ">")
    markdown_text = markdown_text.replace("&amp;", "&")

    return markdown_text.strip(), unhandled_tags


def build_markdown(front_matter: dict, markdown_body: str) -> str:
    """
    Combine the YAML front matter and the Markdown body.
    """
    front_matter_yaml = yaml.dump(front_matter, default_flow_style=False).strip()
    md = f"---\n{front_matter_yaml}\n---\n\n{markdown_body}\n"
    return md


def process_images(
    markdown_text: str,
    source_image_path: Optional[Path],
    target_image_path: Optional[Path],
) -> None:
    """
    Process image links in the Markdown text. For each image link starting with '/assets/images/',
    check if the image exists in the source image directory.
    If it exists and is not already in the target directory, copy it to the target directory.
    Otherwise, print a warning.
    """
    pattern = r"!\[.*?\]\((/assets/images/[^)]+)\)"
    matches = re.findall(pattern, markdown_text)
    for img_path in matches:
        filename = os.path.basename(img_path)
        src_path = source_image_path / filename if source_image_path else None
        tgt_path = target_image_path / filename if target_image_path else None
        if src_path and src_path.exists():
            if tgt_path and not tgt_path.exists():
                try:
                    tgt_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src_path, tgt_path)
                    print(f"\tCopied image: {filename} to target directory.")
                except Exception as e:
                    print_error(f"Error copying {filename}: {e}")
            # else: image already exists in target directory; no action needed.
        else:
            print_warning(f"Warning: Image {filename} not found in source directory.")


def process_file(
    input_path: str,
    output_path: str,
    source_image_path: Optional[Path] = None,
    target_image_path: Optional[Path] = None,
    source_thumbnail_path: Optional[Path] = None,
    target_thumbnail_path: Optional[Path] = None,
) -> Set[str]:
    print(f"\n\nConverting: {input_path} -> {output_path} ...")
    with open(input_path, "r", encoding="utf-8") as f:
        content = f.read()

    front_matter, html_content = parse_front_matter(content)

    # Handle header-img -> thumbnail processing
    input_filename = os.path.basename(input_path)
    if "header-img" in front_matter:
        img_filename = os.path.basename(front_matter["header-img"])
        front_matter["thumbnail"] = f"/assets/images/thumbnails/{img_filename}"
        del front_matter["header-img"]
        if source_thumbnail_path and target_thumbnail_path:
            src_thumb_path = source_thumbnail_path / img_filename
            tgt_thumb_path = target_thumbnail_path / img_filename
            if src_thumb_path.exists():
                tgt_thumb_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_thumb_path, tgt_thumb_path)
                print(
                    f"\tCopied thumbnail: {img_filename} to target thumbnail directory."
                )
            else:
                print_warning(
                    f"header-img {img_filename} not found for file {input_filename}"
                )
    else:
        print_warning(f"no header-img field in file {input_filename}")

    markdown_body, unhandled_tags = convert_html_to_markdown(html_content)
    final_md = build_markdown(front_matter, markdown_body)

    if source_image_path and target_image_path:
        process_images(final_md, source_image_path, target_image_path)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(final_md)
    print(f"Converted: {input_path} -> {output_path}")
    return unhandled_tags


def process_directory(
    input_dir: str,
    output_dir: str,
    source_image_path: Optional[Path] = None,
    target_image_path: Optional[Path] = None,
    source_thumbnail_path: Optional[Path] = None,
    target_thumbnail_path: Optional[Path] = None,
) -> None:
    input_dir_path = Path(input_dir)
    output_dir_path = Path(output_dir)
    output_dir_path.mkdir(parents=True, exist_ok=True)
    all_unhandled_tags = set()
    for file in input_dir_path.iterdir():
        if file.suffix.lower() == ".html":
            output_file = output_dir_path / (file.stem + ".md")
            unhandled_tags = process_file(
                str(file),
                str(output_file),
                source_image_path,
                target_image_path,
                source_thumbnail_path,
                target_thumbnail_path,
            )
            all_unhandled_tags.update(unhandled_tags)

    print(f"\nAll unhandled tags:\n{all_unhandled_tags}\n")


def main() -> None:
    """
    
    Run on single file, copy images:

    python convert_html_to_md.py\
    /path/to/input.html\
    /path/to/output.md\
    --source-image-path /path/to/source_images/\
    --target-image-path /path/to/target_images/

    Run on dir, copy images:

    python convert_html_to_md.py\
    /path/to/input_directory/\
    /path/to/output_directory/\
    --source-image-path /path/to/source_images/\
    --target-image-path /path/to/target_images/
    
    """
    parser = argparse.ArgumentParser(
        description="Convert HTML files to Markdown for Jekyll."
    )
    parser.add_argument("input", help="Input HTML file or directory")
    parser.add_argument("output", help="Output Markdown file or directory")
    parser.add_argument(
        "--source-image-path", help="Source image directory", default=None
    )
    parser.add_argument(
        "--target-image-path", help="Target image directory", default=None
    )
    parser.add_argument(
        "--source-thumbnail-path", help="Source thumbnail image directory", default=None
    )
    parser.add_argument(
        "--target-thumbnail-path", help="Target thumbnail image directory", default=None
    )
    args = parser.parse_args()

    source_image_path: Optional[Path] = (
        Path(args.source_image_path) if args.source_image_path else None
    )
    target_image_path: Optional[Path] = (
        Path(args.target_image_path) if args.target_image_path else None
    )
    source_thumbnail_path: Optional[Path] = (
        Path(args.source_thumbnail_path) if args.source_thumbnail_path else None
    )
    target_thumbnail_path: Optional[Path] = (
        Path(args.target_thumbnail_path) if args.target_thumbnail_path else None
    )

    if target_image_path:
        target_image_path.mkdir(parents=True, exist_ok=True)

    if target_thumbnail_path:
        target_thumbnail_path.mkdir(parents=True, exist_ok=True)

    input_path = Path(args.input)
    output_path = Path(args.output)

    if input_path.is_dir():
        process_directory(
            str(input_path),
            str(output_path),
            source_image_path,
            target_image_path,
            source_thumbnail_path,
            target_thumbnail_path,
        )
    elif input_path.is_file():
        if output_path.is_dir():
            output_file = output_path / (input_path.stem + ".md")
        else:
            output_file = output_path
        process_file(
            str(input_path),
            str(output_file),
            source_image_path,
            target_image_path,
            source_thumbnail_path,
            target_thumbnail_path,
        )
    else:
        print("Invalid input path.")
        sys.exit(1)


if __name__ == "__main__":
    main()
