from pathlib import Path


import json
import re
from datetime import datetime

SCRIPT_PATH = Path(__file__).resolve()
ROOT_PATH = SCRIPT_PATH.parent.parent
POSTS_PATH = ROOT_PATH / "_posts"
HTML_ASSETS_PATH = ROOT_PATH / "assets" / "html"
POSTS_JSON_PATH = HTML_ASSETS_PATH / "site_viewer" / "posts.json"

print(f"\tScript path: {SCRIPT_PATH}")
print(f"\tPosts path: {POSTS_PATH}")
print(f"\tHTML assets path: {HTML_ASSETS_PATH}")
print(f"\tPosts JSON path: {POSTS_JSON_PATH}")


def convert_permalink_to_url(permalink: str) -> str:
    """Converts Jekyll permalink to full URL."""
    base_url = "https://declanoller.github.io"
    return base_url + "/" + permalink


def convert_thumbnail_to_url(thumbnail: str) -> str:
    """Converts thumbnail path to full URL."""
    base_url = "https://declanoller.github.io"
    if thumbnail.startswith("/"):
        return base_url + thumbnail
    else:
        return base_url + "/" + thumbnail


def strip_quotes(s: str) -> str:
    """Strips surrounding quotes from a string, if present."""
    return s.strip('"').strip("'")


def parse_frontmatter(md_path):
    """Extracts frontmatter as a dict from a markdown file."""
    with open(md_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    if not lines or not lines[0].strip().startswith("---"):
        return None
    fm = {}
    i = 1
    while i < len(lines):
        line = lines[i].strip()
        if line == "---":
            break
        if ":" in line:
            key, val = line.split(":", 1)
            fm[key.strip()] = val.strip()
        i += 1
    return fm


def extract_post_info(fm) -> dict[str, str]:
    """Extracts required fields from frontmatter dict."""
    date_str = fm["date"]
    date_only = date_str.split()[0]
    return {
        "date": date_only,
        "post_url": convert_permalink_to_url(fm["permalink"]),
        "thumbnail_url": convert_thumbnail_to_url(fm["thumbnail"]),
        "title_text": strip_quotes(fm["title"]),
    }


def get_all_posts(posts_path):
    posts = []
    for md_file in posts_path.glob("*.md"):
        fm = parse_frontmatter(md_file)
        assert fm, f"Failed to parse frontmatter in {md_file}"

        post_info = extract_post_info(fm)
        posts.append(post_info)

    return posts


def sort_posts(posts):
    def date_key(post):
        try:
            return datetime.strptime(post["date"], "%Y-%m-%d")
        except Exception:
            return datetime.min

    return sorted(posts, key=date_key, reverse=True)


def posts_equal(a, b):
    if len(a) != len(b):
        return False
    for d1, d2 in zip(a, b):
        if d1 != d2:
            return False
    return True


def main():
    posts = get_all_posts(POSTS_PATH)
    posts_sorted = sort_posts(posts)
    if not POSTS_JSON_PATH.exists():
        print("\n\t⚠️ posts.json does not exist; creating new file.")
        with open(POSTS_JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(posts_sorted, f, indent=2)
        print("\t✅➕✅ posts.json created!")
        return
    # If exists, compare
    with open(POSTS_JSON_PATH, "r", encoding="utf-8") as f:
        try:
            old_posts = json.load(f)
        except Exception:
            old_posts = []
    if not posts_equal(posts_sorted, old_posts):
        print("\n\t👴🏻 👴🏻 👴🏻 posts.json is outdated; updating file...")
        with open(POSTS_JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(posts_sorted, f, indent=2)
        print("\t✅✅✅ posts.json updated!")
    else:
        print("\n\t✨🎯⚡ posts.json is up to date; no changes needed.")


if __name__ == "__main__":
    main()
    print()
