#!/usr/bin/env python3
import argparse
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

import requests

# 🔧 Hardcoded path to the local folder where images will be saved
IMAGE_ASSETS_DIR = Path(
    "/home/declan/Documents/code/declanoller.github.io/assets/images"
)  # <-- change this


def find_jpg_urls(text: str) -> list[str]:
    """
    Find all http/https URLs ending in .jpg (optionally with query params).
    """
    pattern = re.compile(
        r'(https?://[^\s)"]+?\.jpg(?:\?[^\s)"]*)?)',
        re.IGNORECASE,
    )
    return pattern.findall(text)


def find_png_urls(text: str) -> list[str]:
    """
    Find all http/https URLs ending in .png (optionally with query params).
    """
    pattern = re.compile(
        r'(https?://[^\s)"]+?\.png(?:\?[^\s)"]*)?)',
        re.IGNORECASE,
    )
    return pattern.findall(text)


def download_image(url: str, dest_dir: Path) -> Path | None:
    """
    Download image from URL into dest_dir, keeping the original filename.
    Returns the local path or None on failure.
    """
    parsed = urlparse(url)
    img_name = Path(parsed.path).name  # keeps e.g. "image.jpg"
    dest_path = dest_dir / img_name

    print(f"  Downloading: {url}")
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
    except Exception as e:
        print(f"  ❌ Failed to download {url}: {e}")
        return None

    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path.write_bytes(resp.content)
    print(f"  ✅ Saved to: {dest_path}")
    return dest_path


def process_markdown(md_path: Path) -> None:
    print(f"Reading markdown file: {md_path}")
    if not md_path.is_file():
        print(f"❌ Error: file not found: {md_path}")
        sys.exit(1)

    text = md_path.read_text(encoding="utf-8")

    print("Searching for .jpg URLs...")
    urls = find_jpg_urls(text) + find_png_urls(text)
    if not urls:
        print(f"No .jpg or .png URLs found. Nothing to do. {urls = }")
        return

    print(f"Found {len(urls)} .jpg URL(s).")

    # We’ll process each URL in the order found
    updated_text = text
    for url in urls:
        print(f"\nProcessing URL: {url}")
        local_path = download_image(url, IMAGE_ASSETS_DIR)
        if local_path is None:
            print("  Skipping replacement due to download failure.")
            continue

        img_name = local_path.name
        new_ref = f"/assets/images/{img_name}"
        print(f"  Replacing in markdown:\n    {url}\n    -> {new_ref}")
        updated_text = updated_text.replace(url, new_ref)

    print(f"\nWriting updated markdown back to: {md_path}")
    md_path.write_text(updated_text, encoding="utf-8")
    print("Done.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download .jpg images from a markdown file and "
        "rewrite their URLs to /assets/images/<img_name>."
    )
    parser.add_argument("markdown_path", help="Path to the .md file")
    args = parser.parse_args()

    md_path = Path(args.markdown_path)
    print(f"Markdown path provided: {md_path}")
    print(f"Using image assets folder: {IMAGE_ASSETS_DIR}")

    process_markdown(md_path)


if __name__ == "__main__":
    main()
