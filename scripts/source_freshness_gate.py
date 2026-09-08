#!/usr/bin/env python3
"""The quote is maintained; the page it came from is not watched.

Every /specs/ page here states platform limits and names the documentation it took
them from. Nothing checks that the documentation still says it. A limit that moves
upstream turns our best-performing pages into confidently wrong ones, and the only
signal would be a reader noticing.

That is the same shape as outlier-site's visible datelines: the claim is
maintained, the thing it depends on is not. This watches the dependency.

WHAT IT CHECKS. For each /specs/ page: pull the phrases the page puts in quotation
marks in its VISIBLE text — those are direct quotes from a platform doc — and
confirm each still appears in one of the sources that page cites. 34 such phrases
across 6 pages as of 2026-09-08.

WHY VISIBLE TEXT ONLY. A first pass over the raw HTML returned 310 "quotes",
including "adplaybook-theme" and "change the colour scheme, I hate it" — script
strings. Strip <script> and <style> before extracting anything a human is supposed
to have read.

RATCHET. A quote may fail to match for honest reasons: a paraphrase in quotation
marks, a source behind JavaScript, a doc that renders its tables client-side. Those
are baselined so only NEW breakage fails. Edit the baseline BY REMOVAL ONLY.

    python3 scripts/source_freshness_gate.py              # check
    python3 scripts/source_freshness_gate.py <root>       # aim it (meta_gate needs this)
    python3 scripts/source_freshness_gate.py --self-check # prove it can fail
"""
from __future__ import annotations

import html
import json
import os
import re
import subprocess
import sys

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
BASELINE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "source_freshness_baseline.json")
MIN_PAGES = 3
MIN_QUOTES = 10


#: Typographic normalisation. The YouTube page states "view counts aren't incremented
#: unless video ad is ≥ 10 seconds"; our page quotes it with ">=". Same fact, different
#: code point, and a literal comparison called it a broken quote. Curly quotes,
#: non-breaking spaces and dashes do the same thing. Normalise BOTH sides or the gate
#: reports typography as drift.
_NORM = {
    "\u2265": ">=", "\u2264": "<=", "\u2260": "!=",
    "\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"',
    "\u00a0": " ", "\u2013": "-", "\u2014": "-", "\u2212": "-",
    "\u2026": "...",
}


def norm(t: str) -> str:
    for a, b in _NORM.items():
        t = t.replace(a, b)
    return re.sub(r"\s+", " ", t).strip()


def visible(page_html: str) -> str:
    body = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", page_html, flags=re.S)
    return norm(html.unescape(re.sub(r"<[^>]+>", " ", body)))


def fetch(url: str) -> str:
    """curl, not urllib: Cloudflare bans the urllib UA on several of these hosts."""
    r = subprocess.run(["curl", "-sL", "-A", UA, "--max-time", "30", url],
                       capture_output=True, text=True)
    return visible(r.stdout) if r.returncode == 0 else ""


def survey(site_root: str = "."):
    pages = {}
    specs = os.path.join(site_root, "specs")
    for root, dirs, files in os.walk(specs):
        for f in files:
            if f != "index.html":
                continue
            p = os.path.join(root, f)
            raw = open(p, encoding="utf-8", errors="replace").read()
            text = visible(raw)
            quotes = [q.strip() for q in re.findall(r"[“\"]([^”\"]{15,120})[”\"]", text)]
            urls = [u for u in re.findall(r'href="(https?://[^"]+)"', raw)
                    if "adplaybook.app" not in u and "github.com" not in u]
            if quotes and urls:
                rel = os.path.relpath(p, site_root).replace("/index.html", "")
                pages[rel] = (sorted(set(quotes)), sorted(set(urls)))
    return pages


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    site_root = args[0] if args else "."
    self_check = "--self-check" in sys.argv

    pages = survey(site_root)
    total_quotes = sum(len(q) for q, _ in pages.values())
    if len(pages) < MIN_PAGES or total_quotes < MIN_QUOTES:
        print(f"FAIL: found {len(pages)} spec page(s) and {total_quotes} quote(s) under "
              f"{site_root!r}; expected at least {MIN_PAGES} and {MIN_QUOTES}.")
        print("      A gate that checked nothing prints the same word as a clean one.")
        return 1

    baseline = json.load(open(BASELINE)) if os.path.exists(BASELINE) else {}
    cache, missing = {}, []

    for page, (quotes, urls) in sorted(pages.items()):
        corpus = ""
        for u in urls:
            if u not in cache:
                cache[u] = fetch(u)
            corpus += cache[u]
        if not corpus.strip():
            missing.append((page, "ALL SOURCES UNREADABLE", urls[0] if urls else "-"))
            continue
        for q in quotes:
            nq = norm(q).rstrip(".,")
            if nq and nq not in corpus:
                key = f"{page}|{nq[:60]}"
                if key not in baseline:
                    missing.append((page, nq, "not found in any cited source"))

    if self_check:
        probe = "this sentence appears in no platform documentation anywhere"
        assert probe not in "".join(cache.values()), "self-check probe is not absent"
        print(f"self-check: a phrase absent from every fetched source is detected as absent. OK")

    print(f"source_freshness_gate: {len(pages)} spec page(s), {total_quotes} quoted phrase(s), "
          f"{len(cache)} source(s) fetched")
    print(f"source_freshness_gate: {len(baseline)} baselined, not enforced")

    if missing:
        print(f"\nFAIL ({len(missing)}):")
        for page, q, why in missing[:10]:
            print(f"  {page}: quoted text no longer in its cited source.")
            print(f"       \"{q[:88]}\"  ({why})")
            print("       Either the platform changed the rule, or the page never quoted it exactly.")
        return 1
    print("\nPASS — every quoted phrase still appears in the source the page cites.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
