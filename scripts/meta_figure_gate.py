#!/usr/bin/env python3
"""A price in a meta description must be a price on the page.

Ported from outlier-site 2026-09-08, where a page's body said "$1,080" (five places,
exact arithmetic) while its meta description, og:description AND JSON-LD
Article.description all said "near $1,100" -- published, indexed, and invisible to all
24 gates there, because every text check reaches a page through a tag-strip and that one
line deletes meta content and drops JSON-LD wholesale. Both are what a search engine and
an AI crawler quote first.

MEASURED HERE FIRST, and the answer is why this ships as prevention rather than a fix:
58 pages, all 58 carrying a meta description, 50 carrying JSON-LD, ALL 58 mentioning
money in the body -- and ZERO putting a figure in a description. That is an editorial
pattern, not luck, and nothing enforces it.

This site has the history that makes it worth enforcing. og.png advertised $19 for twelve
days after the price became $129, through a drift audit that read the HTML and passed.
A price in a description is the same shape: a copy of the number in a position no check
looks at, going stale on its own schedule.

THE VACUITY GUARD IS ON REACH, NOT ON FINDINGS. The outlier-site original guards on
"pages carrying money in a description", which is fine where seven do. Here none do, and
a guard counting those would fail on a clean site forever. What must be proven is that
the scan can SEE descriptions at all -- so it counts pages with a description parsed.
A gate whose guard counts findings cannot tell "nothing wrong" from "nothing read".

    python3 scripts/meta_figure_gate.py              # check
    python3 scripts/meta_figure_gate.py <root>       # aim it
    python3 scripts/meta_figure_gate.py --self-check # prove it can fail
"""
from __future__ import annotations

import html
import json
import os
import re
import sys

BASELINE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "meta_figure_baseline.json")
MIN_DESCRIBED = 40      # vacuity guard -- see the note in main()

MONEY = re.compile(r"\$\d[\d,]*(?:\.\d\d)?")
#: the meta names whose content is quoted back to a reader
DESCRIPTIVE = re.compile(r"(?i)(description|title)")


def amount(fig: str) -> str:
    """Compare money by VALUE, not by typography.

    Added after sweeping the same meta/JSON-LD position for non-money claims. RAM
    figures produced 22 findings and every one was formatting: the body writes
    "16 GB", the description writes "16GB", same fact. Money escaped that because
    this site writes "$1,080" consistently -- but nothing enforces the comma, and a
    description saying "$1080" against a body saying "$1,080" would have been
    reported as a contradiction that is not one. Strip the separators and compare
    the number.
    """
    value = fig.lstrip("$").replace(",", "")
    try:
        return f"{float(value):.2f}"
    except ValueError:
        return fig


def body_text(raw: str) -> str:
    """What a reader sees -- the same tag-strip every other gate uses, on purpose."""
    b = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", raw, flags=re.S)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", b)))


def described(raw: str):
    """(where, text) for every description a crawler reads: meta, og, and JSON-LD."""
    out = []
    for m in re.finditer(r"<meta\b([^>]*)>", raw, re.I):
        attrs = m.group(1)
        key = re.search(r'(?:name|property)\s*=\s*"([^"]*)"', attrs, re.I)
        val = re.search(r'content\s*=\s*"([^"]*)"', attrs, re.I)
        if key and val and DESCRIPTIVE.search(key.group(1)):
            out.append((f"meta {key.group(1)}", html.unescape(val.group(1))))
    for m in re.finditer(r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>',
                         raw, re.S | re.I):
        blob = m.group(1)
        try:
            data = json.loads(blob)
        except Exception:
            # A gate that silently skips what it cannot parse is a gate that reports
            # clean on a broken file. Fall back to the raw text rather than skipping.
            out.append(("JSON-LD (unparsed)", blob))
            continue
        stack = [data]
        while stack:
            node = stack.pop()
            if isinstance(node, dict):
                for k, v in node.items():
                    if isinstance(v, (dict, list)):
                        stack.append(v)
                    elif isinstance(v, str) and DESCRIPTIVE.search(k):
                        out.append((f"JSON-LD {k}", v))
            elif isinstance(node, list):
                stack.extend(node)
    return out


def survey(site_root: str = "."):
    """(page, where, figure) for each description figure missing from the body."""
    bad, with_desc = [], 0
    for root, _d, files in os.walk(site_root):
        if any(x in root for x in (".git", "_seo_build", "scripts", "node_modules")):
            continue
        for f in sorted(files):
            if not f.endswith(".html") or ".pre" in f:
                continue
            path = os.path.join(root, f)
            rel = os.path.relpath(path, site_root)
            raw = open(path, encoding="utf-8", errors="replace").read()
            seen = {amount(x) for x in MONEY.findall(body_text(raw))}
            described_here = described(raw)
            page_described = bool(described_here)
            for where, text in described_here:
                figs = MONEY.findall(text)
                for fig in figs:
                    if amount(fig) not in seen:
                        bad.append((rel, where, fig, text[:90]))
            if page_described:
                with_desc += 1
    return bad, with_desc


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    site_root = args[0] if args else "."

    if "--self-check" in sys.argv:
        probe = ('<meta name="description" content="near $1,100 a year">'
                 '<p>the total is $1,080 a year</p>')
        found = {f for _w, t in described(probe) for f in MONEY.findall(t)}
        assert found == {"$1,100"}, f"self-check: description figures not read: {found}"
        assert "$1,100" not in set(MONEY.findall(body_text(probe))), \
            "self-check: a tag-stripped body still shows the meta figure"
        assert "$1,080" in set(MONEY.findall(body_text(probe))), \
            "self-check: the body figure was lost"
        ld = '<script type="application/ld+json">{"description": "costs $7"}</script>'
        assert ("JSON-LD description", "costs $7") in described(ld), \
            "self-check: JSON-LD description not read"
        assert "$7" not in body_text(ld), "self-check: JSON-LD leaked into the body text"
        assert amount("$1,080") == amount("$1080") == "1080.00", \
            "self-check: the comma is being treated as part of the number"
        assert amount("$20") == amount("$20.00") == "20.00", \
            "self-check: cents normalisation is wrong"
        assert amount("$20") != amount("$2"), \
            "self-check: normalisation collapses different amounts — the first version of " \
            "this helper used rstrip('.0'), which turns $20.00 into $2"
        print("self-check: meta and JSON-LD figures are read, neither reaches the body text "
              "the other gates use, and $1,080/$1080 compare equal while $20/$2 do not. OK")

    bad, with_desc = survey(site_root)
    if with_desc < MIN_DESCRIBED:
        print(f"FAIL: only {with_desc} page(s) under {site_root!r} have a description this "
              f"gate could read; expected at least {MIN_DESCRIBED}.")
        print("      Guarded on REACH, not on findings: this site legitimately puts no price")
        print("      in a description, so counting those could never tell a clean site from")
        print("      an unread one.")
        return 1

    baseline = json.load(open(BASELINE)) if os.path.exists(BASELINE) else {}
    new = [b for b in bad if f"{b[0]}|{b[2]}" not in baseline]

    print(f"meta_figure_gate: {with_desc} page(s) with a readable description; "
          f"{len(bad)} figure(s) in one are not in the body it describes")
    print(f"meta_figure_gate: {len(baseline)} baselined")

    if new:
        print(f"\nFAIL ({len(new)} new):")
        for rel, where, fig, text in new[:8]:
            print(f"  {rel}: {where} says {fig}, which is not on the page.")
            print(f"       \"{text}\"")
            print("       This is what a search engine and an AI crawler quote, and no")
            print("       other gate can see it — they all reach the page through a")
            print("       tag-strip, which deletes meta content and JSON-LD alike.")
        return 1
    print("\nPASS — every figure in a description is a figure on its page.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
