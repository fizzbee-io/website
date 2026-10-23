#!/usr/bin/env bash
# Tell IndexNow (Bing, Yandex, Naver, Seznam; feeds Copilot and much of
# ChatGPT search) which fizzbee.io URLs changed. Run AFTER a deploy is live.
#
# Self-contained: fetches the live sitemap and diffs it against the sitemap
# from the last notification (.indexnow-state.xml, gitignored local state).
# Submitted: new URLs, URLs with a changed <lastmod>, and URLs that
# disappeared from the sitemap (IndexNow accepts deletions so engines
# re-crawl and drop them). The state file is updated only after the
# endpoint accepts, so delivery is at-least-once: a dropped connection
# after acceptance means the same batch is resent next run, which is
# harmless. A fresh checkout (no state file) submits every sitemap URL.
#
# Usage: ./notify-indexnow.sh [--dry-run]
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
case "${1:-}" in
  "") DRY_RUN=0 ;;
  --dry-run) DRY_RUN=1 ;;
  *) echo "usage: notify-indexnow.sh [--dry-run]" >&2; exit 2 ;;
esac

python3 - "$REPO_ROOT" "$DRY_RUN" <<'EOF'
import json
import sys
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

repo_root = Path(sys.argv[1])
dry_run = sys.argv[2] == "1"

HOST = "fizzbee.io"
KEY = "9d8ee5f40a10cc0b2e5ac6deb7cd31b1"  # served from static/<KEY>.txt
STATE = repo_root / ".indexnow-state.xml"
ENDPOINT = "https://api.indexnow.org/IndexNow"


def entries(xml_text):
    """{url: lastmod-or-empty} for each <url> in a sitemap, namespace-agnostic."""
    root = ET.fromstring(xml_text)
    out = {}
    for url in root.iter():
        if url.tag.rsplit("}", 1)[-1] != "url":
            continue
        fields = {child.tag.rsplit("}", 1)[-1]: (child.text or "").strip() for child in url}
        if fields.get("loc"):
            out[fields["loc"]] = fields.get("lastmod", "")
    return out


live = urllib.request.urlopen(f"https://{HOST}/sitemap.xml", timeout=30).read().decode()
new = entries(live)
if not new:
    sys.exit("error: live sitemap has no <url> entries; refusing to proceed")
old = entries(STATE.read_text()) if STATE.exists() else {}

added_or_updated = [u for u, m in new.items() if u not in old or old[u] != m]
removed = [u for u in old if u not in new]
changed = sorted(added_or_updated + removed)

if not changed:
    print("IndexNow: no new, changed or removed URLs since last notification")
    sys.exit(0)

payload = {
    "host": HOST,
    "key": KEY,
    "keyLocation": f"https://{HOST}/{KEY}.txt",
    "urlList": changed,
}
print(f"IndexNow: {len(added_or_updated)} new/updated, {len(removed)} removed"
      + (" (dry run)" if dry_run else ""))
for u in changed:
    print(f"  {'-' if u in removed else '+'} {u}")
if dry_run:
    sys.exit(0)

req = urllib.request.Request(
    ENDPOINT,
    data=json.dumps(payload).encode(),
    headers={"Content-Type": "application/json; charset=utf-8"},
)
status = urllib.request.urlopen(req, timeout=30).status
if status not in (200, 202):
    sys.exit(f"IndexNow returned {status}")
STATE.write_text(live)
print(f"IndexNow: accepted ({status}); state updated")
EOF
