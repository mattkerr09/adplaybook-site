#!/usr/bin/env python3
"""Quality gates for a generated site.

Programmatic SEO has two failure modes and both are fatal. The set of pages can
read as machine-made even when each page reads fine on its own — same skeleton,
same opening move, same headings — and that is what a thin-content penalty
actually is. And a comparison page can state something about a third party that
nobody checked, which is a legal problem rather than a ranking one.

The sibling project's review of its own comparison pages found 891 extracted
claims about competitors, none independently verified, six of them legal or
security allegations. This runs before publish so that cannot happen here.

    python _build/check.py
"""

from __future__ import annotations

import html
import pathlib
import re
import sys
from collections import Counter

SITE = pathlib.Path(__file__).resolve().parents[1]

# Named third parties. Saying a competitor exists is fine; stating their
# pricing, features or policy as fact is what this is looking for.
THIRD_PARTIES = [
    "AdCreative", "Creatify", "Pencil", "Segwise", "Canva", "Jasper",
    "Smartly", "DoubleVerify", "Integral Ad Science", "Ziflow", "MarkUp",
]
# Words that turn a mention into an assertion about them.
ASSERTIVE = re.compile(
    r"\b(costs?|charges?|prices?|priced|\$\d|per month|/mo|does not|cannot|"
    r"fails? to|lacks?|only offers?|limited to)\b", re.I)


def visible(h: str) -> str:
    h = re.sub(r"(?s)<(script|style)[^>]*>.*?</\1>", " ", h)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", h))).strip()


def main() -> int:
    pages = sorted(SITE.glob("**/index.html"))
    if not pages:
        print("no pages built"); return 1

    fails: list[str] = []
    warns: list[str] = []

    openings, h2sets, lengths = [], [], {}
    for p in pages:
        raw = p.read_text()
        rel = "/" + str(p.relative_to(SITE)).replace("index.html", "")
        text = visible(raw)
        lengths[rel] = len(text)

        # 1. Every page must have the head fields that make it citable.
        for field in ('rel="canonical"', "<title>", 'name="description"',
                      'name="last-modified"'):
            if field not in raw:
                fails.append(f"{rel}: missing {field}")

        # 2. Thin pages.
        if len(text) < 900:
            warns.append(f"{rel}: only {len(text)} chars of visible text")

        # 3. Corpus sameness — the failure a per-page check cannot see.
        body = text
        m = re.search(r"</h1>(.{0,200})", raw, re.S)
        if m:
            openings.append(visible(m.group(1))[:60])
        h2sets.append(tuple(sorted(re.findall(r"<h2[^>]*>(.*?)</h2>", raw, re.S))))

        # 4. Assertions about named third parties.
        for name in THIRD_PARTIES:
            for sent in re.split(r"(?<=[.!?])\s+", body):
                if name.lower() in sent.lower() and ASSERTIVE.search(sent):
                    fails.append(
                        f"{rel}: states something about {name} as fact — "
                        f'"{sent[:110]}"')

    # Same opening sentence across many pages reads as a template.
    for opening, n in Counter(openings).most_common(3):
        if n > 2 and opening:
            warns.append(f'{n} pages open with the same words: "{opening[:50]}"')

    # Identical H2 skeletons across many pages.
    for skeleton, n in Counter(h2sets).most_common(3):
        if n > 3 and skeleton:
            warns.append(f"{n} pages share an identical H2 skeleton "
                         f"({len(skeleton)} headings)")

    # 5. Class names used in HTML but never defined in the stylesheet.
    #
    # Renaming a CSS class silently unstyles every page that still uses the old
    # name — the build succeeds, the check passed, and the pages render as
    # unstyled text. That happened here when the stylesheet was rewritten:
    # panel, grid and cta survived in the generators and matched nothing.
    css_src = (SITE / "_build" / "render.py").read_text()
    css = css_src[css_src.index('CSS = """'):
                  css_src.index('"""', css_src.index('CSS = """') + 10)]
    defined = set(re.findall(r"\.([a-z][a-z0-9-]*)", css))
    used = set()
    for p_ in pages:
        for m in re.findall(r'class="([^"]+)"', p_.read_text()):
            used.update(m.split())
    for name in sorted(used - defined):
        fails.append(f"class .{name} is used in HTML but defined nowhere in the CSS")

    # 6. Files a crawler needs.
    for f in ("robots.txt", "sitemap.xml", "llms.txt", "CNAME"):
        if not (SITE / f).exists():
            fails.append(f"missing {f}")

    # 7. Every built page must be in the sitemap, or it does not exist.
    smap = (SITE / "sitemap.xml").read_text() if (SITE / "sitemap.xml").exists() else ""
    for p in pages:
        rel = "/" + str(p.relative_to(SITE)).replace("index.html", "")
        if f"<loc>https://adplaybook.app{rel}</loc>" not in smap:
            fails.append(f"{rel}: not in sitemap.xml")

    print(f"checked {len(pages)} pages\n")
    for w in warns:
        print(f"  WARN  {w}")
    for f in fails:
        print(f"  FAIL  {f}")
    if not warns and not fails:
        print("  clean")
    print(f"\n{len(fails)} failure(s), {len(warns)} warning(s)")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
