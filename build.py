"""
build.py - Static site generator for the portfolio.

Renders every page via Flask's test client and writes the HTML to _site/.
Static assets are copied from static/ into _site/static/.

Works as a clean build (first run) or incremental overwrite (subsequent runs).

Usage:
    python build.py

Render Static Site config:
    Build command:   pip install -r requirements.txt && python build.py
    Publish dir:     _site
"""

import os
import shutil
import yaml
from app import app

OUT_DIR = "_site"


def load_tool_slugs():
    with open("data/tools.yaml", encoding="utf-8") as f:
        tools = yaml.safe_load(f) or []
    return [t["slug"] for t in tools]


def copy_static_assets():
    """Copy static/ into _site/static/, overwriting existing files."""
    src = "static"
    dst = os.path.join(OUT_DIR, "static")
    if not os.path.exists(src):
        return
    if os.path.exists(dst):
        # Overwrite in place: walk source and copy each file
        for root, dirs, files in os.walk(src):
            rel_root = os.path.relpath(root, src)
            dst_root = os.path.join(dst, rel_root)
            os.makedirs(dst_root, exist_ok=True)
            for fname in files:
                shutil.copy2(os.path.join(root, fname), os.path.join(dst_root, fname))
    else:
        shutil.copytree(src, dst)
    print("  %-42s _site/static/" % "(static assets)")


def write_page(client, route, out_path):
    """Fetch a route from the Flask test client and write to disk."""
    response = client.get(route)
    if response.status_code != 200:
        print("  WARNING %s: %s" % (response.status_code, route))
        return False
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "wb") as f:
        f.write(response.data)
    rel = os.path.relpath(out_path, OUT_DIR)
    print("  %-42s _site/%s" % (route, rel))
    return True


def build():
    print("\nBuilding static site -> %s/\n" % OUT_DIR)

    # 1. Ensure output directory exists
    os.makedirs(OUT_DIR, exist_ok=True)

    # 2. Copy static assets
    copy_static_assets()
    print("")

    # 3. Build the page list
    #    Routes map to clean URL folders: /tools -> _site/tools/index.html
    #    Render Static Site serves directory index files at clean URLs.
    slugs = load_tool_slugs()

    pages = [
        # (flask_route,             output_path)
        ("/",          os.path.join(OUT_DIR, "index.html")),
        ("/tools",     os.path.join(OUT_DIR, "tools", "index.html")),
        ("/build-log", os.path.join(OUT_DIR, "build-log", "index.html")),
        ("/about",     os.path.join(OUT_DIR, "about", "index.html")),
    ]

    for slug in slugs:
        pages.append((
            "/tools/%s" % slug,
            os.path.join(OUT_DIR, "tools", slug, "index.html"),
        ))

    # 4. Render each page
    success = 0
    with app.test_client() as client:
        for route, out_path in pages:
            if write_page(client, route, out_path):
                success += 1

        # 5. Render 404 page by triggering a real 404
        resp = client.get("/__build_404__")
        if resp.status_code == 404:
            out_path = os.path.join(OUT_DIR, "404.html")
            with open(out_path, "wb") as f:
                f.write(resp.data)
            print("  %-42s _site/404.html" % "(404 page)")
            success += 1

    total = len(pages) + 1  # +1 for 404
    print("\n  %d/%d pages built." % (success, total))
    if success < total:
        print("  Check warnings above -- some pages may be missing.")
    else:
        print("  All pages built. Deploy: point Render Static Site at _site/")
    print("")


if __name__ == "__main__":
    build()
