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
import html
import os
import re
import sys
import shutil
from pathlib import Path
from typing import Any, Optional, Tuple, Set
import xml.etree.ElementTree as ET

import yaml
from bs4 import BeautifulSoup, NavigableString, Comment, Doctype
import requests
import subprocess

# Define Python keywords for code detection.
PYTHON_KEYWORDS = ["def ", "import ", "class ", "print(", "in range("]
WORDPRESS_EXPORT_MEDIA_XML_FILE = Path(
    "/home/declan/Documents/code/wordpress_site_export/wordpress_export_media.xml"
)

BASE_SITE_PATH = Path("/home/declan/Documents/code/declanoller.github.io")
BASE_ASSETS_PATH = BASE_SITE_PATH / "assets"
IMAGE_ASSETS_PATH = BASE_ASSETS_PATH / "images"
VIDEO_ASSETS_PATH = BASE_ASSETS_PATH / "videos"
IMAGE_ASSETS_PATH.mkdir(parents=True, exist_ok=True)
VIDEO_ASSETS_PATH.mkdir(parents=True, exist_ok=True)


def xml_to_dict(elem):
    d = {elem.tag: {}}
    # Add attributes
    d[elem.tag].update(elem.attrib)

    # Add children or text
    children = list(elem)
    if children:
        child_dict = {}
        for child in children:
            child_result = xml_to_dict(child)
            for key, value in child_result.items():
                if key in child_dict:
                    if not isinstance(child_dict[key], list):
                        child_dict[key] = [child_dict[key]]
                    child_dict[key].append(value)
                else:
                    child_dict[key] = value
        d[elem.tag].update(child_dict)
    else:
        text = elem.text.strip() if elem.text else ""
        if text:
            d[elem.tag] = text if not d[elem.tag] else {"_text": text, **d[elem.tag]}

    return d


def parse_xml_file(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    return xml_to_dict(root)


WORDPRESS_EXPORT_MEDIA_XML_ITEM_DICT_LIST = parse_xml_file(
    WORDPRESS_EXPORT_MEDIA_XML_FILE
)["rss"]["channel"]["item"]
POST_ID_KEY = "{http://wordpress.org/export/1.2/}post_id"
WORDPRESS_POST_ID_TO_THUMBNAIL_NAME = {
    int(d[POST_ID_KEY]): d["guid"]["_text"]
    for d in WORDPRESS_EXPORT_MEDIA_XML_ITEM_DICT_LIST
    if POST_ID_KEY in d and "guid" in d and "_text" in d["guid"]
}


def print_info(msg: str) -> None:
    print(f"\033[92m{msg} \033[0m")


def print_warning(msg: str) -> None:
    print(f"\033[93m{msg} \033[0m")


def print_error(msg: str) -> None:
    print(f"\033[91m{msg} \033[0m")


def is_inline_math_expression(text: str) -> bool:
    """
    Determine whether the given text appears to be a LaTeX/MathJax math expression.
    We consider it math if it starts and ends with a '$'.
    """
    if text.startswith("$") and text.endswith("$"):
        return True
    return False


def is_block_math_expression(text: str) -> bool:
    """
    Determine whether the given text appears to be a LaTeX/MathJax math expression.
    We consider it math if it starts and ends with a '$$'.
    """
    if text.startswith("$$") and text.endswith("$$"):
        return True
    return False


def parse_front_matter(text: str) -> Tuple[dict[str, Any], str]:
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
        keys_to_keep = ["layout", "title", "date", "header-img", "meta", "permalink"]
        front_matter = {k: v for k, v in data.items() if k in keys_to_keep}
        # Force the layout to always be "post"
        front_matter["layout"] = "post"

        # Convert to permalink style with dashes
        front_matter["permalink"] = (
            front_matter["permalink"].strip("/").replace("/", "-")
            # front_matter["permalink"].replace("/", "-", 3).rstrip("/")
        )

        text = text[match.end() :]
    return front_matter, text


def update_image_src(src: str) -> str:
    """
    Update the image source from the old template path to the new /assets/images/ folder.
    Example: '{{ site.baseurl }}/assets/special_9x9_ss.png' becomes '/assets/images/special_9x9_ss.png'
    """
    # new_src = re.sub(r"\{\{\s*site\.baseurl\s*\}\}/assets/", "/assets/images/", src)
    # Strip out anything after assets/ in the original src
    new_src = re.sub(r"\{\{\s*site\.baseurl\s*\}\}/assets/.*/", "/assets/images/", src)
    return new_src


def is_probably_python(code_text: str) -> bool:
    """
    A heuristic to decide if the code in a <pre> block is Python.
    Checks for common Python keywords.
    """
    return any(kw in code_text for kw in PYTHON_KEYWORDS)


def clean_malformed_html(html_text: str) -> str:
    """
    Cleans malformed HTML with misplaced tags (e.g., <p> before <html>) and doctype issues.
    Returns cleaned HTML string.
    """

    # Step 1: Remove DOCTYPEs, wherever they appear
    html_text = re.sub(r"<!DOCTYPE[^>]*>", "", html_text, flags=re.IGNORECASE)

    # Step 2: Remove anything before the first <html> tag
    html_match = re.search(r"<html.*?>", html_text, flags=re.IGNORECASE)
    if html_match:
        html_text = html_text[html_match.start() :]
    else:
        # If there's no <html>, fallback to raw parse
        pass

    # Step 3: Parse with BeautifulSoup to allow structural cleanup
    soup = BeautifulSoup(html_text, "html.parser")

    # Step 4: Remove any <p> that wraps the <html> or comes after </html>
    # Usually this happens because of improperly closed tags around <html>
    for tag in soup.find_all("p"):
        if tag.find("html") or tag.find("body"):
            tag.unwrap()  # unwrap just removes the <p> tag, keeps contents

    # Step 5: Optional — ensure only one <html> and <body> exists
    # BeautifulSoup auto-nests oddly if malformed input has duplicates
    # This step is light, since the earlier cleanup prevents the worst
    # return soup.prettify()
    return str(soup)


def maybe_convert_declanoller_url_to_permalink(url: str) -> str:
    """
    Convert a URL containing 'declanoller.com' to a Jekyll permalink format.
    """
    if "declanoller.com" in url:
        # Extract the part after the domain
        match = re.search(r"declanoller\.com/(\d{4}/\d{2}/\d{2}/.+)", url)
        if match:
            permalink = match.group(1).replace("/", "-", 3).rstrip("/")
            return f"{{{{ site.baseurl }}}}/{permalink}"

    return url


def download_and_convert_video_to_gif(video_url: str) -> str:
    """
    Downloads a video from a URL, converts it to a GIF using ffmpeg, and returns the path to the GIF.

    Args:
        video_url (str): The URL of the video to download.
        video_target_dir (str): The directory to save the downloaded video.
        gif_target_dir (str): The directory to save the converted GIF.

    Returns:
        str: The path to the converted GIF.
    """

    # Download the video
    video_filename = video_url.split("/")[-1]
    video_path = VIDEO_ASSETS_PATH / video_filename

    if video_path.exists():
        print_info(f"\tVideo file {video_path} already exists; skipping download")
    else:
        print_info(f"\tDownloading video {video_url} ...")
        response = requests.get(video_url, stream=True)
        if response.status_code == 200:
            with open(video_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
        else:
            raise Exception(f"Failed to download video from {video_url}")

    # Convert the video to a GIF using ffmpeg
    gif_filename = video_path.stem + ".gif"
    gif_path = IMAGE_ASSETS_PATH / gif_filename

    if gif_path.exists():
        print_info(f"\tConverted gif {gif_path} already exists; skipping conversion")
    else:
        print_info(f"\tConverting {video_path} to gif...")
        ffmpeg_command = [
            "ffmpeg",
            "-i",
            str(video_path),
            "-vf",
            "fps=10,scale=320:-1:flags=lanczos",
            "-c:v",
            "gif",
            str(gif_path),
        ]
        subprocess.run(ffmpeg_command, check=True)

    return str(gif_path)


def remove_doctype_declaration(html_text: str) -> str:
    """
    Remove the DOCTYPE declaration if it matches the specified HTML 4.0 Transitional DTD.
    """
    return re.sub(
        r'<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN" "http://www.w3.org/TR/REC-html40/loose.dtd">',
        "",
        html_text,
        flags=re.IGNORECASE,
    )


def remove_wp_comment_paragraphs(html_text: str) -> str:
    """
    Remove entire <p> tags that contain WordPress-style comments.
    """
    soup = BeautifulSoup(html_text, "html.parser")
    for comment in soup.find_all(string=lambda t: isinstance(t, Comment)):
        if "wp:" in comment:
            if comment.parent and comment.parent.name == "p":
                comment.parent.decompose()
    return str(soup)


def remove_latexpage_first_paragraph(html_text: str) -> str:
    """
    Remove <p>[latexpage]</p> if it is the very first paragraph.
    """
    soup = BeautifulSoup(html_text, "html.parser")
    first_p = soup.find("p")
    if first_p and first_p.get_text(strip=True) == "[latexpage]":
        first_p.decompose()
    return str(soup)


def remove_latexpage_br_in_paragraphs(html_text: str) -> str:
    """
    Remove [latexpage]<br /> at the very beginning of a <p> tag and keep the rest.
    """
    soup = BeautifulSoup(html_text, "html.parser")
    for p in soup.find_all("p"):
        if p.contents and isinstance(p.contents[0], NavigableString):
            if "[latexpage]" in p.contents[0]:
                p.contents[0].replace_with(p.contents[0].replace("[latexpage]", ""))
        for br in p.find_all("br"):
            br.extract()
    return str(soup)


def underline_span_to_h5_heading(html_text: str) -> str:
    """
    Convert underlined text created with <p><span style="text-decoration: underline;">...</span></p>
    to Markdown H5 headings.
    """
    soup = BeautifulSoup(html_text, "html.parser")
    for p in soup.find_all("p"):
        children = list(p.children)
        if len(children) == 1 and getattr(children[0], "name", None) == "span":
            span = children[0]
            if span.has_attr("style") and "text-decoration: underline" in span["style"]:
                heading_text = span.get_text(strip=True)
                md_heading = f"##### {heading_text}\n\n"
                p.replace_with(NavigableString(md_heading))
    return str(soup)


def strong_underline_span_to_h5_heading(html_text: str) -> str:
    """
    In a few instances we have: <p><strong><span style="text-decoration: underline;">...</span></strong></p>
    convert this to Markdown H5 headings.
    """
    soup = BeautifulSoup(html_text, "html.parser")
    for p in soup.find_all("p"):
        children = list(p.children)
        if len(children) == 1 and getattr(children[0], "name", None) == "strong":
            strong = children[0]
            children2 = list(strong.children)
            if len(children2) == 1 and getattr(children2[0], "name", None) == "span":
                span = children2[0]
                if (
                    span.has_attr("style")
                    and "text-decoration: underline" in span["style"]
                ):
                    heading_text = span.get_text(strip=True)
                    md_heading = f"##### {heading_text}\n\n"
                    p.replace_with(NavigableString(md_heading))
    return str(soup)


def underline_span_to_bold(html_text: str) -> str:
    """
    Convert any <span style="text-decoration: underline;">...</span> to Markdown bold.
    """
    soup = BeautifulSoup(html_text, "html.parser")
    for span in soup.find_all("span"):
        if span.has_attr("style") and "text-decoration: underline" in span["style"]:
            bold_text = f"**{span.get_text(strip=True)}**"
            span.replace_with(NavigableString(bold_text))
    return str(soup)


def heading_tags_to_markdown(html_text: str) -> str:
    """
    Convert heading tags (<h2> to <h6>) to Markdown header syntax.
    """
    soup = BeautifulSoup(html_text, "html.parser")
    for level in range(2, 7):
        for header in soup.find_all(f"h{level}"):
            header_text = header.get_text(separator=" ", strip=True)
            md_header = f"{'#' * level} {header_text}\n\n"
            header.replace_with(NavigableString(md_header))
    return str(soup)


def blockquote_to_markdown(html_text: str) -> str:
    """
    Convert <blockquote> tags to Markdown blockquotes.
    """
    soup = BeautifulSoup(html_text, "html.parser")
    for blockquote in soup.find_all("blockquote"):
        blockquote_text = blockquote.get_text(separator="\n", strip=True)
        lines = blockquote_text.splitlines()
        md_blockquote = "\n".join(["> " + line for line in lines]) + "\n\n"
        blockquote.replace_with(NavigableString(md_blockquote))
    return str(soup)


def italic_tags_to_markdown(html_text: str) -> str:
    """
    Convert italic tags (<i> and <em>) to Markdown italics.
    """
    soup = BeautifulSoup(html_text, "html.parser")
    for tag in list(soup.find_all(["i", "em"])):
        italic_text = tag.get_text()
        md_italic = f"*{italic_text}*"
        tag.replace_with(NavigableString(md_italic))
    return str(soup)


def strong_tags_to_markdown(html_text: str) -> str:
    """
    Convert <strong> tags to Markdown bold.
    """
    soup = BeautifulSoup(html_text, "html.parser")
    for tag in list(soup.find_all("strong")):
        strong_text = tag.get_text()
        md_strong = f"**{strong_text}**"
        tag.replace_with(NavigableString(md_strong))
    return str(soup)


def unordered_lists_to_markdown(html_text: str) -> str:
    """
    Convert unordered lists (<ul> with <li>) to Markdown bullet lists.
    """
    soup = BeautifulSoup(html_text, "html.parser")
    for ul in list(soup.find_all("ul")):
        items = []
        for li in ul.find_all("li", recursive=False):
            for a in li.find_all("a"):
                if a.has_attr("href"):
                    markdown_link = f"[{a.get_text(strip=True)}]({a['href']})"
                    a.replace_with(markdown_link)
            li_text = li.get_text(separator="", strip=True)
            items.append(f"- {li_text}")
        md_ul = "\n".join(items) + "\n\n"
        ul.replace_with(NavigableString(md_ul))
    return str(soup)


def ordered_lists_to_markdown(html_text: str) -> str:
    """
    Convert ordered lists (<ol> with <li>) to Markdown numbered lists.
    """
    soup = BeautifulSoup(html_text, "html.parser")
    for ol in list(soup.find_all("ol")):
        items = []
        for idx, li in enumerate(ol.find_all("li", recursive=False), start=1):
            for a in li.find_all("a"):
                if a.has_attr("href"):
                    markdown_link = f"[{a.get_text(strip=True)}]({a['href']})"
                    a.replace_with(markdown_link)
            li_text = li.get_text(separator="", strip=True)
            items.append(f"{idx}. {li_text}")
        md_ol = "\n".join(items) + "\n\n"
        ol.replace_with(NavigableString(md_ol))
    return str(soup)


def pre_tags_to_markdown(html_text: str) -> str:
    """
    Convert <pre> tags (code blocks) to Markdown fenced code blocks.
    """
    soup = BeautifulSoup(html_text, "html.parser")
    for pre in soup.find_all("pre"):
        code_text = pre.get_text()  # preserves whitespace and indentation
        language = "python" if is_probably_python(code_text) else ""
        code_text = code_text.strip("\n")
        md_code = f"```{language}\n{code_text}\n```\n"
        pre.replace_with(NavigableString(md_code))
    return str(soup)


def img_tags_to_markdown(html_text: str) -> str:
    """
    Convert <img> tags to Markdown image syntax.
    """
    soup = BeautifulSoup(html_text, "html.parser")
    for img in soup.find_all("img"):
        src = img.get("src", "")
        new_src = update_image_src(src)
        alt = img.get("alt", "")
        md_img = f"![{alt}]({new_src})"
        img.replace_with(NavigableString(md_img))
    return str(soup)


def a_tags_to_markdown(html_text: str) -> str:
    """
    Convert <a> tags to Markdown hyperlink syntax.
    """
    soup = BeautifulSoup(html_text, "html.parser")
    for a in soup.find_all("a"):
        href = a.get("href", "")
        link_text = a.text
        href = maybe_convert_declanoller_url_to_permalink(href)
        md_link = f"[{link_text}]({href})"
        a.replace_with(NavigableString(md_link))
    return str(soup)


def paragraphs_to_markdown(html_text: str) -> str:
    """
    Convert <p> tags to Markdown, handling math expressions and replacements.
    """
    soup = BeautifulSoup(html_text, "html.parser")
    max_inline_eqn_length = 30
    for p in soup.find_all("p"):
        text = p.get_text(strip=True)
        if is_block_math_expression(text):
            eq = text.strip("$").strip()
            eq = eq.replace("|", " \\mid ")
            new_text = f"$${eq}$$\n"
        elif text.count("$") >= 2:
            """
            print_warning(f"\nHas inline math exprs:\n\t{text}")
            # Search for inline math expressions within the paragraph
            inline_math_matches = re.finditer(r"\$(.+?)\$", text)
            for match in inline_math_matches:
                eq = match.group(1).strip()
                if len(eq) >= max_inline_eqn_length:
                    continue
                print_info(f"\n\tInline math expr:\n\t\t{match.group(1)}")
                eq = eq.replace(
                    "|", " \\mid "
                )  # Replace vertical bar with " \mid " (with spaces)
                new_eq = f"${eq}$"
                print_info(f"\tConverted to:\n\t\t{new_eq}\n")
                text = text.replace(match.group(0), new_eq)

            print_info(f"\nParagraph converted to:\n\t{new_text}\n")
            """
            new_text = text
        else:
            new_text = "".join(str(child) for child in p.contents).strip() + "\n\n"

        new_text = new_text.replace("\\mathrm{log}", "\\log ")
        new_text = new_text.replace("\\textrm{log}", "\\log ")
        new_text = new_text.replace("\\textrm{ln}", "\\log ")
        new_text = new_text.replace("\\textrm{argmax}", "\\arg\\max")
        new_text = new_text.replace("\\textrm{max}", "\\max")
        new_text = new_text.replace("\\textrm{min}", "\\min")

        p.replace_with(NavigableString(new_text))
    return str(soup)


def process_video_blocks_to_gif(html_text: str) -> str:
    """
    Process video blocks and convert them to GIFs.
    """
    soup = BeautifulSoup(html_text, "html.parser")
    for video_tag in soup.find_all(string=re.compile(r"\[video.*?\[/video\]")):
        video_match = re.search(r'mp4="([^"]+)"', video_tag)
        if video_match:
            video_url = video_match.group(1)
            print_info(f"\n\tFound video URL: {video_url}")
            try:
                gif_path = download_and_convert_video_to_gif(video_url)
                gif_filename = Path(gif_path).name
                markdown_image = f"![](/assets/images/{gif_filename})\n\n"
                video_tag.replace_with(NavigableString(markdown_image))
            except Exception as e:
                print_error(f"\n\t\tError processing video {video_url}: {e}")
    return str(soup)


def special_text_replacements(html_text: str) -> str:
    """
    This function is a placeholder for any special text replacements.

    Be careful where you place this -- I'm placing it last, to act as
    a special catch-all.

    Here's a list of the current ones and their reasons:
    - " | " to " \\mid ": This is in the Haskell post and the REPL post, in
                the context of q(x | y), etc.
    """
    # Replace any special text patterns here
    # For example, replace "foo" with "bar"
    html_text = html_text.replace(" | ", r" \mid ")
    return html_text


def find_unhandled_html_tags(html_text: str) -> Set[str]:
    """
    Identify any remaining (unhandled) HTML tags in the given HTML text.
    Excludes common inline tags like <br>.

    Args:
        html_text (str): The HTML content to analyze.

    Returns:
        Set[str]: A set of unhandled HTML tag names.
    """
    soup = BeautifulSoup(html_text, "html.parser")
    unhandled_tags = {tag.name for tag in soup.find_all() if tag.name not in ["br"]}
    if unhandled_tags:
        print_warning(
            f"\n\tWarning: The following HTML tags were not explicitly handled: {', '.join(unhandled_tags)}"
        )
    return unhandled_tags


def remove_remaining_html_tags_and_entities(html_text: str) -> str:
    """
    Remove any remaining HTML tags and replace HTML entities with their literal characters.
    """
    intermediate = re.sub(r"<[^>]+>", "", html_text)
    intermediate = re.sub(r"\n{3,}", "\n\n", intermediate)
    intermediate = intermediate.replace("&lt;", "<")
    intermediate = intermediate.replace("&gt;", ">")
    intermediate = intermediate.replace("&amp;", "&")
    return intermediate.strip()


def convert_html_to_markdown(html_text: str) -> Tuple[str, Set[str]]:
    """
    Convert the HTML content into Markdown.
    Also prints a warning (once per file) for any unhandled HTML tags.
    Returns a tuple of the Markdown text and a set of unhandled tag names.
    """

    # Clean up malformed HTML, because there's some ugly stuff in the old HTML files.
    html_text = clean_malformed_html(html_text)

    soup = BeautifulSoup(html_text, "html.parser")

    # Remove the DOCTYPE declaration if it matches the specified HTML 4.0 Transitional DTD.
    # <!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN" "http://www.w3.org/TR/REC-html40/loose.dtd">
    doctype = soup.find(
        string=lambda text: isinstance(text, NavigableString)
        and text.strip().startswith("<!DOCTYPE html")
    )
    if doctype and "-//W3C//DTD HTML 4.0 Transitional//EN" in doctype:
        doctype.extract()

    html_text = str(soup)

    # Remove entire <p> tags that contain WordPress-style comments.
    html_text = remove_wp_comment_paragraphs(html_text)

    # Remove <p>[latexpage]</p> if it is the very first paragraph.
    html_text = remove_latexpage_first_paragraph(html_text)

    # Remove [latexpage]<br /> at the very beginning of a <p> tag and keep the rest.
    html_text = remove_latexpage_br_in_paragraphs(html_text)

    # Convert underlined text created with <p><span style="text-decoration: underline;">...</span></p>
    # to Markdown H5 headings.
    html_text = underline_span_to_h5_heading(html_text)

    # Convert <p><strong><span style="text-decoration: underline;">...</span></strong></p>
    # to Markdown H5 headings.
    html_text = strong_underline_span_to_h5_heading(html_text)

    # Convert any <span style="text-decoration: underline;">...</span> to Markdown bold.
    html_text = underline_span_to_bold(html_text)

    # Convert heading tags (<h2> to <h6>) to Markdown header syntax.
    html_text = heading_tags_to_markdown(html_text)

    # Convert <blockquote> tags to Markdown blockquotes.
    html_text = blockquote_to_markdown(html_text)

    # Convert italic tags (<i> and <em>) to Markdown italics.
    html_text = italic_tags_to_markdown(html_text)

    # Convert <strong> tags to Markdown bold.
    html_text = strong_tags_to_markdown(html_text)

    # Convert unordered lists (<ul> with <li>) to Markdown bullet lists.
    html_text = unordered_lists_to_markdown(html_text)

    # Convert ordered lists (<ol> with <li>) to Markdown numbered lists.
    html_text = ordered_lists_to_markdown(html_text)

    # Convert <pre> tags (code blocks) to Markdown fenced code blocks.
    html_text = pre_tags_to_markdown(html_text)

    # Convert <img> tags to Markdown image syntax.
    html_text = img_tags_to_markdown(html_text)

    # Convert <a> tags to Markdown hyperlink syntax.
    html_text = a_tags_to_markdown(html_text)

    # Convert <p> tags to Markdown, handling math expressions and replacements.
    html_text = paragraphs_to_markdown(html_text)

    # Process video blocks and convert them to GIFs.
    html_text = process_video_blocks_to_gif(html_text)

    # Perform any special text replacements.
    html_text = special_text_replacements(html_text)

    # Find any unhandled HTML tags
    unhandled_tags = find_unhandled_html_tags(html_text)

    # Remove any remaining HTML tags and replace HTML entities with their literal characters.
    html_text = remove_remaining_html_tags_and_entities(html_text)

    return html_text.strip(), unhandled_tags


def build_markdown(front_matter: dict, markdown_body: str) -> str:
    """
    Combine the YAML front matter and the Markdown body.
    """
    front_matter_yaml = yaml.dump(front_matter, default_flow_style=False).strip()
    md = f"---\n{front_matter_yaml}\n---\n\n{markdown_body}\n"
    return md


def process_images(
    markdown_text: str,
    source_image_path: Path,
    target_image_path: Path,
) -> None:
    """
    Process image links in the Markdown text. For each image link starting with '/assets/images/',
    check if the image exists in the source image directory.
    If it exists and is not already in the target directory, copy it to the target directory.
    Otherwise, print a warning.
    """

    target_image_path.mkdir(parents=True, exist_ok=True)

    pattern = r"!\[.*?\]\((/assets/images/[^)]+)\)"
    matches = re.findall(pattern, markdown_text)

    matches_set = set([Path(m).name for m in matches])
    image_locations = {}
    for root, _, files in os.walk(source_image_path):
        for file in files:
            if file in matches_set:
                file_path = Path(root) / file
                if file in image_locations:
                    print_warning(f"Warning: Duplicate image found: {file}")
                image_locations[file] = file_path

    print_info(f"\n\tFound {len(matches)} images in markdown file.")
    print_info(f"\tFound {len(image_locations)} source/target image pairs to process.")

    for img_name, src_path in image_locations.items():
        tgt_path = target_image_path / img_name
        if not tgt_path.exists():
            try:
                shutil.copy2(src_path, tgt_path)
                print(f"\t\tCopied image: {img_name} to target directory.")
            except Exception as e:
                print_error(f"Error copying {img_name}: {e}")
        else:
            print_warning(f"\t\tImage {img_name} already in target directory.")

    """
    for img_path in matches:
        filename = os.path.basename(img_path)
        src_path = source_image_path / filename
        tgt_path = target_image_path / filename
        if src_path.exists():
            if not tgt_path.exists():
                try:
                    shutil.copy2(src_path, tgt_path)
                    print(f"\tCopied image: {filename} to target directory.")
                except Exception as e:
                    print_error(f"Error copying {filename}: {e}")
            # else: image already exists in target directory; no action needed.
        else:
            print_warning(f"Warning: Image {filename} not found in source directory.")
    """


def process_thumbnail(
    input_path: str,
    html_content: str,
    front_matter: dict[str, Any],
    source_thumbnail_path: Optional[Path] = None,
    target_thumbnail_path: Optional[Path] = None,
) -> None | str:
    thumbnail_error = None

    if not (source_thumbnail_path and target_thumbnail_path):
        return thumbnail_error

    target_thumbnail_path.mkdir(parents=True, exist_ok=True)
    input_filename = os.path.basename(input_path)
    if "header-img" in front_matter:
        # First try to find the thumbnail in the front matter.
        img_filename = os.path.basename(front_matter["header-img"])
        front_matter["thumbnail"] = f"/assets/images/thumbnails/{img_filename}"
        del front_matter["header-img"]
        src_thumb_path = source_thumbnail_path / img_filename
        tgt_thumb_path = target_thumbnail_path / img_filename
        if src_thumb_path.exists():
            tgt_thumb_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_thumb_path, tgt_thumb_path)
            print_info(
                f"\tCopied thumbnail: {img_filename} to target thumbnail directory."
            )
        else:
            thumbnail_error = (
                f"header-img {img_filename} not found for file {input_filename}"
            )
            print_warning(f"\t\t{thumbnail_error}")
    elif "meta" in front_matter and "_thumbnail_id" in front_matter["meta"]:
        # Next, try to find the thumbnail ID in the meta field.
        thumbnail_id = front_matter["meta"]["_thumbnail_id"]
        if isinstance(thumbnail_id, str) and thumbnail_id.isdigit():
            thumbnail_id = int(thumbnail_id)
        print_info(
            f"\tFound thumbnail ID: {thumbnail_id} in meta field for file {input_filename}"
        )

        # Check if the thumbnail ID exists in the WordPress export XML.
        if thumbnail_id in WORDPRESS_POST_ID_TO_THUMBNAIL_NAME:
            thumbnail_name = WORDPRESS_POST_ID_TO_THUMBNAIL_NAME[thumbnail_id]
            print_info(
                f"\tFound thumbnail name: {thumbnail_name} for ID {thumbnail_id} in WordPress export XML."
            )
            img_filename = os.path.basename(thumbnail_name)
            tgt_thumb_path = target_thumbnail_path / img_filename
            front_matter["thumbnail"] = f"/assets/images/thumbnails/{img_filename}"
            if tgt_thumb_path.exists():
                print_info(
                    f"\t\tThumbnail {img_filename} already exists in target directory, skipping"
                )
                return None

            # First try to copy the local file
            src_thumb_path = source_thumbnail_path / img_filename
            if src_thumb_path.exists():
                shutil.copy2(src_thumb_path, tgt_thumb_path)
                print_info(
                    f"\tCopied thumbnail: {img_filename} to target thumbnail directory."
                )
                return None
            # elif thumbnail_name.startswith("https://www.declanoller.com/"):
            elif thumbnail_name.startswith("http"):
                # In this case, we try to download it from the website, this once
                try:
                    response = requests.get(thumbnail_name, stream=True)
                    if response.status_code == 200:
                        with open(tgt_thumb_path, "wb") as f:
                            shutil.copyfileobj(response.raw, f)
                        print_info(
                            f"\tDownloaded thumbnail: {img_filename} to target thumbnail directory."
                        )
                        return None
                    else:
                        thumbnail_error = f"Failed to download thumbnail {thumbnail_name} for file {input_filename}"
                        print_error(f"\t\t{thumbnail_error}")
                except Exception as e:
                    thumbnail_error = (
                        f"Error downloading thumbnail {thumbnail_name}: {e}"
                    )
                    print_error(f"\t\t{thumbnail_error}")
            else:
                thumbnail_error = f"Thumbnail image {img_filename} (ID {thumbnail_id} from export XML) not found for file {input_filename}"
                print_warning(f"\t\t{thumbnail_error}")
        else:
            thumbnail_error = f"Thumbnail ID {thumbnail_id} not found in WordPress export XML for file {input_filename}"
            print_warning(f"\t\t{thumbnail_error}")

        # If the thumbnail ID is not found in the XML, check the HTML content.
        # Search for the thumbnail ID in the <img> tags
        found_thumbnail = False
        soup = BeautifulSoup(html_content, "html.parser")
        for img in soup.find_all("img"):
            img_class = img.get("class", [])
            if any(f"wp-image-{thumbnail_id}" in cls for cls in img_class):
                src = img.get("src", "")
                img_filename = os.path.basename(src)
                front_matter["thumbnail"] = f"/assets/images/thumbnails/{img_filename}"
                found_thumbnail = True
                src_thumb_path = None
                for root, _, files in os.walk(source_thumbnail_path):
                    if img_filename in files:
                        src_thumb_path = Path(root) / img_filename
                        break

                tgt_thumb_path = target_thumbnail_path / img_filename
                if src_thumb_path is not None:
                    shutil.copy2(src_thumb_path, tgt_thumb_path)
                    print_info(
                        f"\tCopied thumbnail: {img_filename} to target thumbnail directory."
                    )
                    return None
                else:
                    thumbnail_error = f"Thumbnail image {src_thumb_path} not found for file {input_filename}"
                    print_error(f"\t\t{thumbnail_error}")
                break

        if not found_thumbnail:
            thumbnail_error = f"Thumbnail with ID {thumbnail_id} not found in <img> tags for file {input_filename}"
            print_error(f"\t{thumbnail_error}")
    else:
        thumbnail_error = (
            f"no header-img or meta->_thumbnail_id field in file {input_filename}"
        )
        print_warning(f"\t{thumbnail_error}")

    return thumbnail_error


def process_file(
    input_path: str,
    output_path: str,
    source_image_path: Optional[Path] = None,
    target_image_path: Optional[Path] = None,
    source_thumbnail_path: Optional[Path] = None,
    target_thumbnail_path: Optional[Path] = None,
) -> dict[str, Any]:
    print(f"\n\nConverting: {input_path} -> {output_path} ...")
    with open(input_path, "r", encoding="utf-8") as f:
        content = f.read()

    front_matter, html_content = parse_front_matter(content)

    thumbnail_error = process_thumbnail(
        input_path,
        html_content,
        front_matter,
        source_thumbnail_path,
        target_thumbnail_path,
    )

    if "meta" in front_matter:
        del front_matter["meta"]

    markdown_body, unhandled_tags = convert_html_to_markdown(html_content)
    final_md = build_markdown(front_matter, markdown_body)

    if source_image_path is not None and target_image_path is not None:
        process_images(final_md, source_image_path, target_image_path)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(final_md)
    print(f"Converted: {input_path} -> {output_path}")
    return {
        "unhandled_tags": unhandled_tags,
        "thumbnail_error": thumbnail_error,
    }


def process_directory(
    input_dir: str,
    output_dir: str,
    source_image_path: Optional[Path] = None,
    target_image_path: Optional[Path] = None,
    source_thumbnail_path: Optional[Path] = None,
    target_thumbnail_path: Optional[Path] = None,
    name_filter: Optional[str] = None,
) -> None:
    input_dir_path = Path(input_dir)
    output_dir_path = Path(output_dir)
    output_dir_path.mkdir(parents=True, exist_ok=True)
    all_unhandled_tags = set()
    processed_files_summary = {}

    for file in input_dir_path.iterdir():
        if file.suffix.lower() == ".html":
            if name_filter and name_filter not in file.name:
                # print(f"Skipping {file.name} (does not match filter '{name_filter}')")
                continue

            output_file = output_dir_path / (file.stem + ".md")
            processed_file_info = process_file(
                str(file),
                str(output_file),
                source_image_path,
                target_image_path,
                source_thumbnail_path,
                target_thumbnail_path,
            )

            all_unhandled_tags.update(processed_file_info["unhandled_tags"])
            processed_files_summary[file.name] = processed_file_info

    print_error("\nSummary of problems with thumbnails:\n")
    for file_name, info in processed_files_summary.items():
        if info["thumbnail_error"]:
            print_warning(f"\nFile: {file_name}:")
            print_error(f"\t{info['thumbnail_error']}")

    print_warning(f"\nAll unhandled tags:\n{all_unhandled_tags}\n")


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
    parser.add_argument(
        "--name-filter", help="Filter by filename contains", default=None, type=str
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
            name_filter=args.name_filter,
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
