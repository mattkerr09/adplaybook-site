#!/usr/bin/env python3
"""Tell the search engines the site changed.

IndexNow pushes new and changed URLs to Bing, Yandex, Seznam and Naver instead
of waiting to be crawled. One POST covers all of them — they share the index.

**Google does not participate.** Google dropped its own sitemap ping endpoint in
2023 and never joined IndexNow, so the only way to nudge it is Search Console,
which needs the account owner signed in. Do not add a fake Google call here and
let it look covered.

The key file must already be live at the site root before submitting, or the
endpoint rejects the batch — so run this after the deploy has finished, not
alongside it.

    python _build/submit.py            # everything in the sitemap
    python _build/submit.py /specs/x/  # just these paths
"""

from __future__ import annotations

import json
import pathlib
import re
import sys
import urllib.error
import urllib.request

SITE = pathlib.Path(__file__).resolve().parents[1]
HOST = "adplaybook.app"
BASE = f"https://{HOST}"
ENDPOINTS = ["https://api.indexnow.org/IndexNow", "https://www.bing.com/indexnow"]


def find_key() -> str:
    """The key is whatever <key>.txt sits in the repo root, and its contents
    must equal its filename. That is the whole authentication scheme."""
    for f in SITE.glob("*.txt"):
        stem = f.stem
        if re.fullmatch(r"[0-9a-f]{8,128}", stem) and f.read_text().strip() == stem:
            return stem
    sys.exit("no IndexNow key file found in the site root")


def main() -> int:
    key = find_key()

    if len(sys.argv) > 1:
        urls = [BASE + p if p.startswith("/") else p for p in sys.argv[1:]]
    else:
        smap = (SITE / "sitemap.xml").read_text()
        urls = re.findall(r"<loc>(.*?)</loc>", smap)
    if not urls:
        sys.exit("nothing to submit")

    # Refuse to submit a key the live site is not serving — a rejected batch
    # that looks like a success is worse than not running.
    probe = f"{BASE}/{key}.txt"
    try:
        with urllib.request.urlopen(probe, timeout=30) as r:
            if r.read().decode().strip() != key:
                sys.exit(f"{probe} does not serve the key")
    except urllib.error.URLError as exc:
        sys.exit(f"{probe} is not reachable ({exc}) — deploy before submitting")

    body = json.dumps({
        "host": HOST, "key": key, "keyLocation": probe, "urlList": urls,
    }).encode()

    ok = True
    for ep in ENDPOINTS:
        req = urllib.request.Request(
            ep, data=body,
            headers={"Content-Type": "application/json; charset=utf-8"})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                print(f"  {r.status}  {ep}  ({len(urls)} urls)")
                ok &= r.status in (200, 202)
        except urllib.error.HTTPError as exc:
            print(f"  {exc.code}  {ep}  — {exc.reason}")
            ok = False

    print("\nGoogle is not covered by this. Submit the sitemap in Search "
          "Console: https://search.google.com/search-console")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
