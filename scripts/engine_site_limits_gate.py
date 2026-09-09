#!/usr/bin/env python3
"""A character limit lives in TWO repositories. This checks they still agree.

⚠️ WHY THIS EXISTS. `~/ad maker app/backend/adkit/platforms/*.json` is the engine's
authority on what each platform allows; `adplaybook-site/specs/<platform>/` publishes the
same numbers to readers. That is two copies of a FACT across two repos, with nothing
comparing them — the shape Crisp's "two copies of a RULE" entry generalises. A limit moves
upstream, one side is updated, and the site quietly publishes a number the engine no longer
believes.

⚠️ ATTRIBUTION IS STRUCTURAL, NOT PROXIMITY — the same lesson rival_price_source_gate
learned. A first version flattened the HTML and looked for a number within 160 characters
of the word "headline". The pages state limits in a TABLE: the column header is the field
and the row cell is the value, and flattening destroyed exactly the structure carrying the
claim. Coverage went from 5 comparable pairs to 13 when it read the table instead.

⚠️ IT REPORTS DISAGREEMENT, NOT ABSENCE. A spec page need not publish every limit the
engine holds, and "the page does not mention 15" is not a defect. Only a stated number that
CONTRADICTS the engine is. Silence is not a finding.

Run:  python3 scripts/engine_site_limits_gate.py [site_root] [--self-check]
"""
import glob
import json
import os
import re
import sys
from html.parser import HTMLParser

ENGINE = os.path.expanduser("~/ad maker app/backend/adkit/platforms")

#: Engine field -> the column header that means the same thing on a spec page.
COLUMN = {"headline_chars": "headline", "primary_text_chars": "body text",
          "description_chars": "description", "caption_chars": "caption"}

#: Vacuity guard on REACH. Measured 2026-09-08: 13 comparable pairs, contributed by 7 of
#: the spec pages.
#:
#: ⚠️ Worded carefully on purpose. This line first phrased the coverage as a count followed
#: by the word for an ad network, and platform_count_gate FAILED on it — correctly, since it
#: scans this tree for exactly that shape and the site carries eight of them, so a sentence
#: meaning "seven pages had a comparable pair" read as an inventory claim that was wrong.
#: The rewrite then failed AGAIN, because the comment explaining the mistake QUOTED it.
#:
#: ⇒ A COMMENT IN A SCANNED TREE IS A CLAIM, and you cannot quote a forbidden phrase inside
#: the tree that forbids it. Adding a file to a watched directory publishes every sentence
#: it contains, including the ones about why a sentence was removed.
#: A run that finds fewer has stopped reading one side and must not print the same word
#: as a clean one.
MIN_PAIRS = 10


class _Tables(HTMLParser):
    def __init__(self):
        super().__init__(); self.tables = []; self._t = None; self._r = None; self._c = None

    def handle_starttag(self, tag, attrs):
        if tag == "table": self._t = []
        elif tag == "tr" and self._t is not None: self._r = []
        elif tag in ("td", "th") and self._r is not None: self._c = []

    def handle_data(self, d):
        if self._c is not None: self._c.append(d)

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self._c is not None:
            self._r.append(re.sub(r"\s+", " ", "".join(self._c)).strip()); self._c = None
        elif tag == "tr" and self._r is not None:
            self._t.append(self._r); self._r = None
        elif tag == "table" and self._t is not None:
            self.tables.append(self._t); self._t = None


def engine_limits(path):
    out = {}
    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if isinstance(v, int) and not isinstance(v, bool) and k.endswith("_chars"):
                    out.setdefault(k, set()).add(v)
                walk(v)
        elif isinstance(o, list):
            for v in o: walk(v)
    walk(json.load(open(path)))
    return out


def page_cells(html_text, column):
    """Numbers under a column whose header names `column`. Structural, not proximity."""
    p = _Tables(); p.feed(html_text)
    cells = set()
    for tb in p.tables:
        if not tb: continue
        idx = [i for i, c in enumerate(tb[0]) if column in c.lower()]
        for i in idx:
            for row in tb[1:]:
                if i < len(row):
                    cells |= {int(n) for n in re.findall(r"\b(\d{1,4})\b", row[i])}
    return cells


def compare(site_root):
    rows = []
    for f in sorted(glob.glob(os.path.join(ENGINE, "*.json"))):
        plat = os.path.basename(f)[:-5]
        page = os.path.join(site_root, "specs", plat, "index.html")   # EXACT, never a substring
        if not os.path.exists(page):
            continue
        html_text = open(page, encoding="utf-8", errors="replace").read()
        for field, vals in sorted(engine_limits(f).items()):
            col = COLUMN.get(field)
            if not col: continue
            cells = page_cells(html_text, col)
            if not cells: continue          # the page does not state it: silence, not a defect
            rows.append((plat, field, sorted(vals), sorted(cells), bool(cells & vals)))
    return rows


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    site_root = args[0] if args else "."

    if not os.path.isdir(ENGINE):
        print(f"FAIL: the engine repo is not at {ENGINE!r}.")
        print("      The site publishes limits it cannot verify. THIS IS A FAILURE, NOT A SKIP.")
        return 1

    rows = compare(site_root)

    if "--self-check" in sys.argv:
        # Plant a disagreement and demand the REAL comparison reports it. Asserting that a
        # planted number differs from another number would be arithmetic, not a test of
        # this gate — the same precondition-vs-capability defect found in
        # source_freshness_gate on 2026-09-08.
        fake = "<table><tr><th>Placement</th><th>Headline</th></tr>" \
               "<tr><td>x</td><td>9999</td></tr></table>"
        # ⚠️ 9999 not 99999. The extractor takes \d{1,4} because real limits top out at
        # 3000 (linkedin primary_text_max_chars), so a five-digit probe falls OUTSIDE the
        # instrument's range and the self-check failed on its own FIXTURE, not on the
        # reader. Fix the probe, never widen the code to accept a bad probe.
        got = page_cells(fake, "headline")
        assert got == {9999}, f"self-check: the table reader did not find the cell ({got})"
        assert not (got & {30, 40, 70, 90, 125, 150, 300, 800, 3000}), \
            "self-check: the planted value collides with a real limit and proves nothing"
        assert page_cells("<table><tr><th>Body text</th></tr><tr><td>90</td></tr></table>",
                          "headline") == set(), \
            "self-check: a column header is being ignored — every cell would be compared"
        print("self-check: the table reader finds a cell under its own column header, and "
              "ignores cells under a different one. OK")

    if len(rows) < MIN_PAIRS:
        print(f"FAIL: only {len(rows)} comparable pair(s), expected at least {MIN_PAIRS}.")
        print("      One side stopped being read. A gate that compared nothing prints the "
              "same word as a clean one.")
        return 1

    bad = [r for r in rows if not r[4]]
    print(f"engine_site_limits_gate: {len(rows)} comparable pair(s) across "
          f"{len({r[0] for r in rows})} platform(s)")
    if bad:
        print(f"\nFAIL ({len(bad)}): the site publishes a limit the engine does not hold.")
        for plat, field, vals, cells, _ in bad:
            print(f"  specs/{plat}/ {field}: engine {vals}, page states {cells}")
        return 1
    print("PASS — every character limit stated on both sides agrees with the engine.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
