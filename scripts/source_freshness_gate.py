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
SELF_PROBE = "this sentence appears in no platform documentation anywhere"
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


def _in_any_source(needle: str, sources: list) -> bool:
    """True if `needle` occurs inside ONE source, never across a join of them.

    Named so the self-check can exercise the real decision on a case derived from the
    problem (a quote spanning a seam must be rejected) rather than re-stating the loop's
    expression. The seam case is not hypothetical -- see the comment at the call site.
    """
    return any(needle in src for src in sources)


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

    #: SELF-CHECK, PLANTED BEFORE THE LOOP SO IT RUNS THE REAL DETECTION PATH.
    #:
    #: ⚠️ The previous self-check asserted only that a probe string was ABSENT from the
    #: fetched corpus, and then printed "a phrase absent from every fetched source is
    #: DETECTED as absent. OK". It never ran the detection. Proved 2026-09-08 by
    #: mutation: replacing `if nq and nq not in corpus:` with `if nq and False:` —
    #: disabling detection ENTIRELY — left the self-check exiting 0 and still printing
    #: that line. It asserted a precondition and claimed a capability.
    #:
    #: This plants a page whose quote cannot appear in any real documentation, lets the
    #: ordinary loop run over it, and afterwards demands the loop REPORTED it. The
    #: assertion is on the observable outcome, not on a re-statement of the loop's own
    #: comparison, so it cannot agree with the implementation by construction.
    SELF_PAGE = "__self_check_planted__"
    if self_check and pages:
        _first_urls = next(iter(sorted(pages.items())))[1][1]
        pages = dict(pages)
        pages[SELF_PAGE] = ([SELF_PROBE], _first_urls)

    for page, (quotes, urls) in sorted(pages.items()):
        corpus = ""
        for u in urls:
            if u not in cache:
                cache[u] = fetch(u)
            corpus += cache[u]
        if not corpus.strip():
            missing.append((page, "ALL SOURCES UNREADABLE", urls[0] if urls else "-"))
            continue
        #: ⚠️ TEST EACH SOURCE SEPARATELY, NEVER THE CONCATENATION.
        #:
        #: This read `if nq and nq not in corpus:` where `corpus` is every cited source
        #: joined end to end. The property is "the quote appears in at least one cited
        #: source", and union-membership is ALMOST equivalent — except at the seam. A
        #: quote spanning the boundary between two joined documents matches the corpus
        #: while appearing in NEITHER, so the gate passes it. Demonstrated 2026-09-08:
        #:     A = "Headlines are limited to 30 characters."
        #:     B = "Descriptions may use 90 characters."
        #:     quote = "30 characters.Descriptions may"   -> in A: False, in B: False,
        #:                                                   in A+B: True
        #: That is a false negative in the one check this gate exists to perform.
        #:
        #: Found by the installed Outlier app (1.11.821, lite) reading this file for the
        #: adplaybook-gate-read bench task, an hour after I edited it and did not see it.
        #: My own task note asserted "no gate joins sources; every join( hit is
        #: os.path.join" — true of the TOKEN and false of the BEHAVIOUR, because the
        #: concatenation is `+=`. I searched for the word; it searched for the effect.
        _sources = [cache[u] for u in urls if cache.get(u)]
        for q in quotes:
            nq = norm(q).rstrip(".,")
            if nq and not _in_any_source(nq, _sources):
                key = f"{page}|{nq[:60]}"
                if key not in baseline:
                    missing.append((page, nq, "not found in any cited source"))

    if self_check:
        # Precondition: the probe really is absent, so a report about it means something.
        assert SELF_PROBE not in "".join(cache.values()), \
            "self-check: the probe is NOT absent from the corpus — it proves nothing"
        # The property, on the observable outcome: the loop must have REPORTED it.
        planted = [m for m in missing if m[0] == SELF_PAGE]
        assert planted, \
            "self-check: DETECTION IS DEAD — a planted phrase absent from every source " \
            "was not reported. The gate would pass a page quoting text no source contains."
        missing = [m for m in missing if m[0] != SELF_PAGE]
        # SEAM REGRESSION — the real decision, on a case derived from the problem.
        _a = "Headlines are limited to 30 characters."
        _b = "Descriptions may use 90 characters."
        _seam = "30 characters.Descriptions may"     # in NEITHER source, in the join
        assert _seam in (_a + _b), "self-check: the seam probe does not span the join"
        assert not _in_any_source(_seam, [_a, _b]), \
            "self-check: A QUOTE SPANNING TWO JOINED SOURCES IS BEING ACCEPTED — the " \
            "gate is testing the concatenation again, and would pass a quote that " \
            "appears in no cited source."
        assert _in_any_source("limited to 30", [_a, _b]), \
            "self-check: a quote genuinely inside one source is being rejected"
        print("self-check: a planted phrase absent from every fetched source was reported "
              "by the real detection path; a seam-spanning quote is rejected and a "
              "genuine one accepted. OK")

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
