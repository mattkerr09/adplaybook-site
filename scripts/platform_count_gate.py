#!/usr/bin/env python3
"""The site says "8 platforms" in a dozen places. Nothing here can count them.

Found 2026-09-08 by looking at og.png with eyes rather than grep. The card carries
no price -- the $19-for-twelve-days incident was fixed by removing the price from
the image entirely, which is a better fix than regenerating it, because a card with
no price cannot go stale on price. But it does carry a COUNT:

    "Every claim traced to a source  ·  8 platforms  ·  Mac"      make_og.py:94

and that count is hand-typed in about a dozen places:

    index.html            "8 platforms" and "Eight platforms" x3
    specs/index.html      title, og:title AND twitter:title, all "for 8 platforms",
                          plus "Eight platforms." in the lede
    _build/render.py      :1802 and :1837
    _build/selfcheck.py   :87, :124, :182
    _build/make_og.py     :94  -- baked into a PNG no text check can read

THE REAL PROBLEM IS NOT THAT IT IS TYPED. It is that the CLAIM AND ITS SOURCE LIVE
IN DIFFERENT REPOSITORIES. render.py's own comment says the spec pages are
"generated straight from backend/adkit/platforms/*.json" -- a path in ~/ad maker app.
This repo carries no copy: _data/ holds one unrelated file. So the tables are derived
and the number describing them is not, and no check inside either repo sees both.

Ship a ninth platform and the spec pages regenerate correctly while a dozen hand-typed
eights go quietly wrong, one of them in an image.

FAILING TO FIND THE APP REPO IS A FAILURE, NOT A PASS. A gate that skips when its
second input is missing reports clean on exactly the day the two repos drift apart.
It says which path it looked for.

    python3 scripts/platform_count_gate.py              # check
    python3 scripts/platform_count_gate.py <site-root>  # aim it
    python3 scripts/platform_count_gate.py --self-check # prove it can fail
"""
from __future__ import annotations

import os
import re
import sys

#: where the specs actually live, relative to $HOME
APP_SPECS = os.path.join(os.path.expanduser("~"), "ad maker app",
                         "backend", "adkit", "platforms")
WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
         "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12}
CLAIM = re.compile(r"(?i)\b(\d{1,2}|" + "|".join(WORDS) + r")\s+platforms\b")
#: A count of platforms is not automatically a claim about OUR coverage.
#: learn/audience-floors-by-platform says "Four platforms publish a hard floor",
#: which is a true statement about what the platforms themselves publish and has
#: nothing to do with how many AdPlaybook reads. The verb is the discriminator: a
#: coverage claim is a bare noun phrase ("Eight platforms.", "for 8 platforms"),
#: while a claim about the world gives the platforms something to do.
ABOUT_THEM = re.compile(r"(?i)^\s*(publish|enforce|require|have|impose|set|report|support|offer|list|state|document)\w*\b")
MIN_CLAIMS = 4          # vacuity guard on REACH: this many claims must be found


def claimed(site_root: str):
    """(file, line, number) for every "N platforms" claim, in pages AND generators."""
    out = []
    for root, dirs, files in os.walk(site_root):
        dirs[:] = [d for d in dirs if d not in (".git", "node_modules", ".venv")]
        for f in sorted(files):
            if not f.endswith((".html", ".py", ".txt", ".md")):
                continue
            if f == os.path.basename(__file__):
                continue
            p = os.path.join(root, f)
            try:
                text = open(p, encoding="utf-8", errors="replace").read()
            except OSError:
                continue
            for m in CLAIM.finditer(text):
                tok = m.group(1).lower()
                n = WORDS.get(tok, None)
                if n is None:
                    try:
                        n = int(tok)
                    except ValueError:
                        continue
                if ABOUT_THEM.match(text[m.end():m.end() + 40]):
                    continue
                line = text.count("\n", 0, m.start()) + 1
                out.append((os.path.relpath(p, site_root), line, n))
    return out


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    site_root = args[0] if args else "."

    if "--self-check" in sys.argv:
        assert CLAIM.search("for 8 platforms") and CLAIM.search("Eight platforms."), \
            "self-check: digit and word forms are not both read"
        assert not CLAIM.search("platforms are listed"), \
            "self-check: a bare mention counts as a claim"
        m = CLAIM.search("Nine platforms")
        assert m and WORDS[m.group(1).lower()] == 9, "self-check: word->number is wrong"
        assert ABOUT_THEM.match(" publish a hard floor"), \
            "self-check: a claim about what platforms DO is not excluded"
        assert not ABOUT_THEM.match(". Every number here is quoted"), \
            "self-check: a coverage claim is being excluded"
        print("self-check: '8 platforms' and 'Eight platforms' both read as 8, "
              "and a bare mention is not a claim. OK")

    found = claimed(site_root)
    if len(found) < MIN_CLAIMS:
        print(f"FAIL: only {len(found)} platform-count claim(s) found under {site_root!r}; "
              f"expected at least {MIN_CLAIMS}.")
        print("      Guarded on reach: a scan that found nothing prints the same word as a "
              "clean one.")
        return 1

    if not os.path.isdir(APP_SPECS):
        print(f"FAIL: cannot verify. The platform specs are not at {APP_SPECS!r}.")
        print(f"      The site makes {len(found)} claim(s) about how many platforms there are "
              f"and carries no copy of the specs, so the answer lives in the other repo.")
        print("      This is a FAILURE and not a skip: a gate that passes when its second "
              "input is missing reports clean on the day the two repos drift apart.")
        return 1

    actual = len([f for f in os.listdir(APP_SPECS) if f.endswith(".json")])
    wrong = [(f, l, n) for f, l, n in found if n != actual]

    print(f"platform_count_gate: {actual} spec file(s) in {APP_SPECS}")
    print(f"platform_count_gate: {len(found)} claim(s) on the site, {len(wrong)} disagreeing")

    if wrong:
        print(f"\nFAIL ({len(wrong)}):")
        for f, l, n in wrong:
            print(f"  {f}:{l} says {n} platforms; there are {actual}.")
        print("\n  Regenerate og.png too — make_og.py bakes the count into the image, and no")
        print("  text check anywhere can read it. That card advertised a stale price for")
        print("  twelve days once; the count is the same shape of claim in the same place.")
        return 1
    print("\nPASS — every platform count on the site matches the specs it describes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
