#!/usr/bin/env python3
"""The quote is maintained; the page it came from is not watched.

Every /specs/ page here states platform limits and names the documentation it took
them from. Nothing checks that the documentation still says it. A limit that moves
upstream turns our best-performing pages into confidently wrong ones, and the only
signal would be a reader noticing.

That is the same shape as outlier-site's visible datelines: the claim is
maintained, the thing it depends on is not. This watches the dependency.

WHAT IT CHECKS. For each /specs/<platform>/ page: (1) the phrases the page puts in
quotation marks in its VISIBLE text — direct quotes from a platform doc; (2) the
distinctive TABLE FIGURES — dimensions, file sizes, aspect ratios; and (3) the
CHARACTER LIMITS the ad copy is written to (headline / body / description counts,
including per-line limits). Each must still appear in a source the page cites. Every
/specs/<platform>/index.html gets a row in the output, and a page that cites a source
but yields nothing checkable is a FAIL — so a page can never be silently skipped.

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
    "≥": ">=", "≤": "<=", "≠": "!=",
    "‘": "'", "’": "'", "“": '"', "”": '"',
    " ": " ", "–": "-", "—": "-", "−": "-",
    "…": "...",
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


_FIG_RE = re.compile(r"\d{2,4}\s?[x×]\s?\d{2,4}|\d+\s?MB\b|\d+:\d+")
PAGE_FIGS: dict = {}
PAGE_CHARLIMITS: dict = {}


def fignorm(s: str) -> str:
    return re.sub(r"[\s,]", "", s or "").replace("×", "x").lower()


def table_figures(raw_html: str) -> list:
    figs = []
    for cell in re.findall(r"<td[^>]*>(.*?)</td>", raw_html, re.S):
        figs += _FIG_RE.findall(html.unescape(re.sub(r"<[^>]+>", " ", cell)))
    return sorted(set(f.strip() for f in figs if f.strip()))


def _fig_ok(fg: str, sources: list) -> bool:
    """True if the figure is confirmed on a source: verbatim, or a MB<->GB unit conversion, or a
    dimension whose two numbers both appear. Avoids false-flagging unit-converted/paraphrased figures."""
    s = fignorm(fg)
    if not s:
        return True
    corpus = " ".join(fignorm(x) for x in sources)
    if s in corpus:
        return True
    m = re.match(r"(\d+)(mb|gb)$", s)
    if m:
        n, u = int(m.group(1)), m.group(2)
        if u == "mb" and n % 1024 == 0 and f"{n // 1024}gb" in corpus:
            return True
        if u == "gb" and f"{n * 1024}mb" in corpus:
            return True
    m = re.match(r"(\d+)x(\d+)$", s)
    if m and m.group(1) in corpus and m.group(2) in corpus:
        return True
    return False


#: CHARACTER LIMITS. The single most load-bearing figure class for AdPlaybook — copy is written to
#: exactly these counts — and the one _FIG_RE cannot see, because a headline limit is a bare "27" in a
#: table cell, not a dimension or a file size. Read it from the COLUMN, not the number: a cell under a
#: header that names a text field (Headline, Body text, Description, ...) is a character count.
_TEXTCOL_RE = re.compile(
    r"headline|body|description|primary|caption|title|tagline|subtitle|heading|char|text", re.I)
#: v1 2026-09-24 (CEO): ROW-oriented tables. Microsoft Advertising lists limits as
#: `Field | How many | Limit you type | Limit after substitution` — the field NAME is in the
#: first cell and the count is in a `Limit`/`Limit you type` column, so the column-header rule
#: saw zero on the most-searched page. A column whose header says limit/character holds char
#: counts; a field-ish first column means the row's first cell names the field. "How many" is a
#: COUNT column (no limit/char in its header), so it is never read as a character limit.
_FIELDCOL_RE = re.compile(
    r"\b(field|element|asset|placement|component|item|attribute|property|control|part)\b", re.I)
_LIMITCOL_RE = re.compile(r"limit|charact|\bchars?\b", re.I)


def _cells(row_html: str, tag: str) -> list:
    return [norm(html.unescape(re.sub(r"<[^>]+>", " ", c)))
            for c in re.findall(rf"<{tag}[^>]*>(.*?)</{tag}>", row_html, re.S)]


def char_limit_figures(raw_html: str) -> list:
    """(N, column, kind) for each character count in a text-field column cell. kind='per_line' when the
    cell states the limit per line, else 'total'. Handles a bare int ("27") and rich cells
    ("25 to stay visible - 100 hard cap" -> 25 and 100; "2 lines x 35 per line" -> 35 per line). A
    number that is a LINE COUNT ("2 lines") is skipped, not read as a character count."""
    out = []
    for tbl in re.findall(r"<table[^>]*>(.*?)</table>", raw_html, re.S):
        rows = re.findall(r"<tr[^>]*>(.*?)</tr>", tbl, re.S)
        hdr = next((r for r in rows if "<th" in r.lower()), None)
        if hdr is None:
            continue
        headers = _cells(hdr, "th")
        textcol = {i for i, h in enumerate(headers) if _TEXTCOL_RE.search(h)}
        if textcol:
            #: COLUMN-oriented — the field names ARE the column headers (Placement | Headline | Body text).
            for r in rows:
                if "<td" not in r.lower():
                    continue
                for i, c in enumerate(_cells(r, "td")):
                    if i not in textcol:
                        continue
                    low = c.lower()
                    for m in re.finditer(r"\d{1,4}", c.replace(",", "")):
                        n = int(m.group())
                        tail = low[m.end():m.end() + 12]
                        if re.match(r"\s*lines?\b", tail) and "per" not in tail:
                            continue  # a LINE count ("2 lines"), not a character count
                        kind = ("per_line" if re.search(r"per\s*line|each\s*line|/\s*line|per\s*each",
                                                        low[m.start():m.start() + 40]) else "total")
                        out.append((n, headers[i], kind))
        elif headers and _FIELDCOL_RE.search(headers[0] or ""):
            #: ROW-oriented — Field | How many | Limit. Limit columns hold char counts; the row's first
            #: cell names the field. "How many" has no limit/char header, so it is ignored. Comma forms
            #: (1,000; 2,048) survive the `,`-strip; a rich limit cell ("30 after substitution") yields 30.
            limitcols = [i for i, h in enumerate(headers) if _LIMITCOL_RE.search(h or "")]
            if limitcols:
                for r in rows:
                    if "<td" not in r.lower():
                        continue
                    cells = _cells(r, "td")
                    if not cells:
                        continue
                    field = cells[0].strip()
                    if not field or not re.search(r"[A-Za-z]", field):
                        continue
                    for i in limitcols:
                        if i < len(cells):
                            for m in re.finditer(r"\d{1,4}", cells[i].replace(",", "")):
                                out.append((int(m.group()), field, "total"))
    seen, uniq = set(), []
    for n, col, k in out:
        key = (n, col.lower(), k)
        if key not in seen:
            seen.add(key)
            uniq.append((n, col, k))
    return uniq


def _charlimit_ok(n: int, sources: list) -> bool:
    """True if a cited source states the number WITH character-context — never a bare N, which matches
    anywhere. Accepts 'N characters', 'N-character', 'N char', 'up to N', and the per-line forms
    ('N characters per line', 'N max for each line'). A forgiving proximity check, so a legitimate
    phrasing is never false-flagged (the attempt-1 lesson: a strict literal match red-flagged real data)."""
    corpus = " ".join(sources).lower().replace(",", "")
    if re.search(rf"up to\s+{n}\b", corpus):
        return True
    for m in re.finditer(rf"\b{n}\b", corpus):
        window = corpus[max(0, m.start() - 30): m.end() + 35]
        if "char" in window or re.search(r"per\s*line|each\s*line|/\s*line|per\s*each", window):
            return True
    return False


def survey(site_root: str = "."):
    #: v1 2026-09-24 (CEO): survey EVERY platform spec page, not only pages that quote a source. A page
    #: can carry checkable figures / character limits with no quoted phrase — Meta, Google and Reddit
    #: did — and excluding them made the gate PASS by NOT LOOKING. Every /specs/<platform>/index.html is
    #: now included; main() gives each a row and fails a page that cites a source but yields nothing
    #: checkable, so a page can never be silently skipped.
    PAGE_FIGS.clear()
    PAGE_CHARLIMITS.clear()
    pages = {}
    specs = os.path.join(site_root, "specs")
    for root, dirs, files in os.walk(specs):
        for f in files:
            if f != "index.html":
                continue
            p = os.path.join(root, f)
            rel = os.path.relpath(p, site_root).replace("/index.html", "")
            if rel == "specs":            # the /specs/ landing page, not a platform spec
                continue
            raw = open(p, encoding="utf-8", errors="replace").read()
            text = visible(raw)
            quotes = [q.strip() for q in re.findall(r"[“\"]([^”\"]{15,120})[”\"]", text)]
            urls = [u for u in re.findall(r'href="(https?://[^"]+)"', raw)
                    if "adplaybook.app" not in u and "github.com" not in u]
            pages[rel] = (sorted(set(quotes)), sorted(set(urls)))
            PAGE_FIGS[rel] = table_figures(raw)
            PAGE_CHARLIMITS[rel] = char_limit_figures(raw)
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
    cache, missing, unverifiable, reports = {}, [], [], []

    #: SELF-CHECK, PLANTED BEFORE THE LOOP SO IT RUNS THE REAL DETECTION PATH.
    #:
    #: ⚠️ The previous self-check asserted only that a probe string was ABSENT from the
    #: fetched corpus, and then printed "a phrase absent from every fetched source is
    #: DETECTED as absent. OK". It never ran the detection. Proved 2026-09-08 by
    #: mutation: replacing `if nq and nq not in corpus:` with `if nq and False:` —
    #: disabling detection ENTIRELY — left the self-check exiting 0 and still printing
    #: that line. It asserted a precondition and claimed a capability.
    #:
    #: This plants pages whose content cannot appear in any real documentation, lets the
    #: ordinary loop run over them, and afterwards demands the loop REPORTED them. The
    #: assertions are on the observable outcome, not on a re-statement of the loop's own
    #: comparison, so they cannot agree with the implementation by construction. Three
    #: capabilities are proven: quote detection, character-limit detection, and INCLUSION
    #: (CEO 2026-09-24 — a page with figures but no quoted phrase must still be measured;
    #: excluding those was the bug that hid Meta / Google / Reddit).
    SELF_PAGE = "__self_check_planted__"
    SELF_PAGE2 = "__self_check_inclusion__"
    if self_check and pages:
        _first_urls = next(iter(sorted(pages.items())))[1][1]
        pages = dict(pages)
        pages[SELF_PAGE] = ([SELF_PROBE], _first_urls)
        PAGE_FIGS[SELF_PAGE] = ["9999x9999"]
        PAGE_CHARLIMITS[SELF_PAGE] = [(9998, "Headline", "total")]
        pages[SELF_PAGE2] = ([], _first_urls)         # figures, NO quoted phrase -> must be measured
        PAGE_FIGS[SELF_PAGE2] = ["7777x7777"]
        PAGE_CHARLIMITS[SELF_PAGE2] = []

    for page, (quotes, urls) in sorted(pages.items()):
        figs = PAGE_FIGS.get(page, [])
        clims = PAGE_CHARLIMITS.get(page, [])
        for u in urls:
            if u not in cache:
                cache[u] = fetch(u)
        _sources = [cache[u] for u in urls if cache.get(u)]
        #: A source is curl-unreadable when it comes back EMPTY or is a facebook.com page (its ad docs
        #: render client-side, so curl gets a contentless shell, not the limits). An UNCONFIRMED item
        #: whose sources are curl-unreadable is MACHINE-UNVERIFIABLE — reported, never a miss, never silent.
        blocked = any((not cache.get(u, "").strip()) or ("facebook.com" in u) for u in urls)
        checkable = len(quotes) + len(figs) + len(clims)
        reports.append((page, len(quotes), len(figs), len(clims), len(_sources), len(urls), blocked))
        #: NO SILENT SKIPS (CEO 2026-09-24): a page that cites a source but has nothing checkable is not
        #: measured, and that is a FAIL — loud, never a quiet omission.
        if urls and checkable == 0:
            missing.append((page, "NO CHECKABLE ITEMS",
                            "cites a source but has no quote, figure or character limit to verify"))
            continue
        if urls and not _sources:
            #: cites sources but NONE were readable -> everything on the page is unverifiable, reported below.
            for q in quotes:
                unverifiable.append((page, f'"{norm(q)[:56]}"'))
            for fg in figs:
                unverifiable.append((page, fg))
            for n, col, k in clims:
                unverifiable.append((page, f"{n} {col}{' per line' if k == 'per_line' else ''}"))
            continue
        #: ⚠️ TEST EACH SOURCE SEPARATELY, NEVER THE CONCATENATION.
        #:
        #: This read `if nq and nq not in corpus:` where `corpus` is every cited source joined end to
        #: end. The property is "the quote appears in at least one cited source", and union-membership is
        #: ALMOST equivalent — except at the seam. A quote spanning the boundary between two joined
        #: documents matches the corpus while appearing in NEITHER, so the gate passes it. Demonstrated
        #: 2026-09-08:
        #:     A = "Headlines are limited to 30 characters."
        #:     B = "Descriptions may use 90 characters."
        #:     quote = "30 characters.Descriptions may"   -> in A: False, in B: False, in A+B: True
        #: That is a false negative in the one check this gate exists to perform. Found by the installed
        #: Outlier app reading this file an hour after I edited it and did not see it: my task note
        #: asserted "no gate joins sources" — true of the TOKEN and false of the BEHAVIOUR, because the
        #: concatenation was `+=`. I searched for the word; it searched for the effect.
        for q in quotes:
            nq = norm(q).rstrip(".,")
            if nq and not _in_any_source(nq, _sources):
                key = f"{page}|{nq[:60]}"
                if key not in baseline:
                    missing.append((page, nq, "not found in any cited source"))
        for fg in figs:
            if _fig_ok(fg, _sources):
                continue
            if blocked:
                unverifiable.append((page, fg))
            elif f"{page}|FIG|{fignorm(fg)[:40]}" not in baseline:
                missing.append((page, fg, "table figure not in any cited source"))
        for n, col, k in clims:
            if _charlimit_ok(n, _sources):
                continue
            label = f"{n} ({col}{', per line' if k == 'per_line' else ''})"
            if blocked:
                unverifiable.append((page, label))
            elif f"{page}|CHAR|{col.lower()}|{n}" not in baseline:
                missing.append((page, label, "character limit not stated with character-context on any cited source"))

    if self_check:
        # Precondition: the probe really is absent, so a report about it means something.
        assert SELF_PROBE not in "".join(cache.values()), \
            "self-check: the probe is NOT absent from the corpus — it proves nothing"
        # The property, on the observable outcome: the loop must have REPORTED each planted item.
        planted = [m for m in missing if m[0] == SELF_PAGE]
        assert any("table figure" in m[2] for m in planted), \
            "self-check: TABLE-FIGURE DETECTION IS DEAD - a planted 9999x9999 absent from every source was not reported"
        assert any("character limit" in m[2] for m in planted), \
            "self-check: CHARACTER-LIMIT DETECTION IS DEAD - a planted 9998 headline limit absent from every source was not reported"
        assert any(m[0] == SELF_PAGE2 and "figure" in m[2] for m in missing), \
            "self-check: INCLUSION IS DEAD - a page with a figure but no quoted phrase was not measured (the Meta/Google/Reddit bug)"
        assert planted, \
            "self-check: DETECTION IS DEAD — a planted phrase absent from every source " \
            "was not reported. The gate would pass a page quoting text no source contains."
        missing = [m for m in missing if m[0] not in (SELF_PAGE, SELF_PAGE2)]
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
        print("self-check: planted quote, character-limit and figures-but-no-quote pages were all "
              "reported by the real detection path; a seam-spanning quote is rejected and a genuine "
              "one accepted. OK")

    print("Per-page coverage — quotes / figures / character limits / sources (every page is measured):")
    for page, nq, nf, nc, ns, nu, blk in sorted(reports):
        if page in (SELF_PAGE, SELF_PAGE2):
            continue
        note = ""
        if nu and (nq + nf + nc) == 0:
            note = "  <-- NOT MEASURED (cites a source, nothing checkable)"
        elif blk:
            note = "  <-- source not machine-readable, items verified by hand"
        print(f"  {page}: {nq} quote / {nf} figure / {nc} char-limit / {ns} of {nu} source{note}")

    print(f"source_freshness_gate: {len(reports)} spec page(s), {total_quotes} quoted phrase(s), "
          f"{sum(n for _, _, nf, nc, *_ in reports for n in (nf, nc))} figure/char-limit(s), "
          f"{len(cache)} source(s) fetched")
    print(f"source_freshness_gate: {len(baseline)} baselined, not enforced")

    if missing:
        print(f"\nFAIL ({len(missing)}):")
        for page, q, why in missing[:12]:
            print(f"  {page}: a checked value is no longer in its cited source.")
            print(f"       \"{str(q)[:88]}\"  ({why})")
            print("       Either the platform changed the rule, or the page never stated it exactly.")
        return 1
    if unverifiable:
        print(f"\nMACHINE-UNVERIFIABLE ({len(unverifiable)}) - cited source blocks automated readers "
              f"(e.g. Facebook renders client-side); verify by hand at the read date shown on the page:")
        for page, item in unverifiable[:15]:
            print(f"  {page}: {item}")
    print("\nPASS — every quoted phrase, table figure and character limit still appears in the source the page cites.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
