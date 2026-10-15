#!/usr/bin/env python3
"""Validate a built copy of fizzbee.io before it is deployed (roadmap 2.2).

Usage:
  python3 tools/check_site.py <path-to-hugo-output>

Failures (exit 1):
  - a page without exactly one canonical tag pointing to itself
  - duplicate titles, descriptions or canonical URLs (minus the allowlists)
  - an internal link to a missing page, or to a missing anchor on a page
  - a sitemap URL with no page in the build or no <lastmod>, or /tags/ in
    the sitemap

Warnings (reported, exit 0):
  - a page with an empty meta description
  - a page without exactly one og:title / og:description / og:image /
    twitter:card

Out of scope, checked elsewhere or exempt by decision:
  - /tags/ pages: robots-disallowed and sitemap-excluded, so metadata rules
    do not apply (e.g. /tags/page/2/ canonicalizes to /tags/).
  - 404.html and privacy.html carry no canonical on purpose.
  - Alias redirect stubs canonicalize to their target, not themselves.
  - /play and /chat are served by Cloud Run, not present in the build.
"""

import html
import os
import re
import sys
from pathlib import Path
from urllib.parse import urljoin, urlsplit

BASE_URL = "https://fizzbee.io"
APP_PATHS = ("/play", "/chat")  # served by Cloud Run, not in the build

# Known, accepted duplicates: title -> exactly the pages allowed to share it.
# Anything else that collides, including a third page with one of these
# titles, is a failure. (The fallback description is shared only with the
# robots-blocked /tags/ pages, which are not scanned, so descriptions have
# no allowlist.)
DUP_TITLE_ALLOW = {
    "Getting Started | FizzBee": {"/design/tutorials/getting-started/",
                                  "/testing/tutorials/getting-started/"},
    "Symmetry Reduction | FizzBee": {"/reference/language/symmetry-reduction/",
                                     "/design/tutorials/symmetry_reduction/"},
}

SKIP_FILES = {"404.html", "privacy.html"}


def allowed_duplicate(allow, value, first_url, url):
    """True only if BOTH colliding pages are on the allowlist for value.

    Checking just the current page would let a stray page that happens to be
    scanned first slip through while the allowed pair collides with it.
    """
    ok = allow.get(value, set())
    return first_url in ok and url in ok


def attrs(tag):
    return dict(re.findall(r'([a-zA-Z:-]+)="([^"]*)"', tag))


def is_alias_stub(html_text):
    return 'http-equiv="refresh"' in html_text and "<body" not in html_text


def page_url(rel):
    url = "/" + rel.replace(os.sep, "/")
    return url[: -len("index.html")] if url.endswith("/index.html") else url


def resolve(page, href):
    """An internal path for href as seen from page, or None if external.

    Handles root-relative (/x/), relative (../x/), same-page fragments (#x)
    and absolute URLs on our own host.
    """
    parts = urlsplit(href)
    if parts.scheme or parts.netloc:
        if f"{parts.scheme}://{parts.netloc}" != BASE_URL:
            return None
        return (parts.path or "/") + ("#" + parts.fragment if parts.fragment else "")
    if href.startswith("//"):
        return None
    resolved = urljoin(page, href)
    return resolved if resolved.startswith("/") else None


def normalize(base):
    """Add a trailing slash to extensionless paths (Hugo pretty URLs)."""
    if base.endswith("/") or "." in base.rsplit("/", 1)[-1]:
        return base
    return base + "/"


def target_file(root, base):
    if base.endswith("/"):
        return root / base.lstrip("/") / "index.html"
    return root / base.lstrip("/")


def scan(root):
    """(pages, failures, warnings) for every non-stub page in the build."""
    pages = {}  # url -> {title, desc, canonicals, anchors, links, rel}
    for path in sorted(root.rglob("*.html")):
        rel = str(path.relative_to(root))
        text = path.read_text(encoding="utf-8", errors="replace")
        if is_alias_stub(text) or rel in SKIP_FILES:
            continue
        if rel.startswith("tags" + os.sep) or rel == os.path.join("tags", "index.html"):
            continue
        url = page_url(rel)
        metas = [attrs(t) for t in re.findall(r"<meta[^>]*>", text)]
        links = [attrs(t) for t in re.findall(r"<link[^>]*>", text)]
        title = re.search(r"<title>([^<]*)</title>", text)
        pages[url] = {
            "rel": rel,
            "title": html.unescape(title.group(1)) if title else "",
            "desc": next((html.unescape(m.get("content", "")) for m in metas
                          if m.get("name") == "description"), ""),
            "og": {k: sum(1 for m in metas if m.get("property") == k)
                   for k in ("og:title", "og:description", "og:image")},
            "twitter": sum(1 for m in metas if m.get("name") == "twitter:card"),
            "canonicals": [l.get("href") for l in links if l.get("rel") == "canonical"],
            "anchors": set(re.findall(r'id="([^"]+)"', text)),
            "hrefs": [attrs(t).get("href", "") for t in re.findall(r"<a[^>]*>", text)],
        }
    return pages


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__.strip().splitlines()[0] + f"\nusage: check_site.py <path-to-hugo-output>")
    root = Path(sys.argv[1])
    if not (root / "index.html").exists():
        sys.exit(f"error: {root} doesn't look like Hugo output")

    pages = scan(root)
    failures, warnings = [], []

    # Canonicals: exactly one, pointing to the page itself.
    seen_canon, seen_title, seen_desc = {}, {}, {}
    for url, p in pages.items():
        expected = BASE_URL + url
        if p["canonicals"] != [expected]:
            failures.append(f"{url}: canonical is {p['canonicals']}, expected [{expected}]")
        for value, seen, allow in (
            (p["canonicals"] and p["canonicals"][0], seen_canon, {}),
            (p["title"], seen_title, DUP_TITLE_ALLOW),
            (p["desc"], seen_desc, {}),
        ):
            if not value:
                continue
            if value in seen and not allowed_duplicate(allow, value, seen[value], url):
                failures.append(f"duplicate: {value[:80]!r} on {seen[value]} and {url}")
            seen.setdefault(value, url)
        if not p["desc"].strip():
            warnings.append(f"{url}: empty meta description")
        for k, n in {**p["og"], "twitter:card": p["twitter"]}.items():
            if n != 1:
                warnings.append(f"{url}: {k} x{n}")

    # Internal links and anchors.
    link_failures = set()
    for url, p in pages.items():
        for href in p["hrefs"]:
            internal = resolve(url, href)
            if internal is None:
                continue
            base, _, frag = internal.partition("#")
            base = normalize(base) if base else url
            if base.startswith(APP_PATHS):
                continue
            if not target_file(root, base).exists():
                link_failures.add(f"{url}: link to missing page {href}")
            elif frag and base in pages and frag not in pages[base]["anchors"]:
                link_failures.add(f"{url}: link to missing anchor {href}")
    failures.extend(sorted(link_failures))

    # Sitemap.
    sitemap = root / "sitemap.xml"
    if sitemap.exists():
        sm = sitemap.read_text()
        entries = re.findall(r"<url>(.*?)</url>", sm, re.S)
        for entry in entries:
            loc = re.search(r"<loc>([^<]+)</loc>", entry)
            loc = loc.group(1) if loc else ""
            path = normalize(loc.replace(BASE_URL, "") or "/")
            if "/tags/" in loc:
                failures.append(f"sitemap: contains {loc}")
            if not target_file(root, path).exists():
                failures.append(f"sitemap: no page in build for {loc}")
            if "<lastmod>" not in entry:
                failures.append(f"sitemap: no lastmod for {loc}")
        print(f"sitemap: {len(entries)} URLs")
    else:
        failures.append("sitemap.xml missing from build")

    print(f"pages checked: {len(pages)}")
    for w in warnings:
        print(f"warning: {w}", file=sys.stderr)
    if failures:
        for f in failures:
            print(f"FAIL: {f}", file=sys.stderr)
        sys.exit(f"{len(failures)} failures, {len(warnings)} warnings")
    print(f"site check passed ({len(warnings)} warnings)")


if __name__ == "__main__":
    main()
