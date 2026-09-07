#!/usr/bin/env python3
"""One row per page: what query is this title, and can the body answer it?

SEO order (5), 2026-09-07. The site has 558 impressions, 0 clicks and an
average position of 66 — so every page is being SHOWN for something and chosen
for nothing, and the question worth asking per page is the one the order names:

    what exact query is this page's title, and does the body answer it better
    than the page currently ranking?

WHAT THIS CAN AND CANNOT MEASURE, stated up front because half the question is
outside this machine. It CANNOT see a SERP, so it cannot answer "better than
the page currently ranking" — anything claiming to would be inventing a
comparison. What it measures instead:

    earns        impressions from Search Console, where we have them (7 queries)
    query-shaped is the title a phrase somebody would type, or a label?
    answers      does the body answer it in the first 300 characters, where an
                 answer engine looks — or only somewhere further down?
    sourced      does the page carry a number AND its attribution, the pair
                 docket's _is_specific requires

A page that is query-shaped, answers early and is sourced is doing everything
this site can do from here. The rest is the SERP's business.

Written to _build/, which Jekyll excludes from the served site — verified:
/_build/content.py returns 404. This repo is public and serves tracked files,
so an internal working table does not belong at the root.

    python3 _build/query_table.py          # print
    python3 _build/query_table.py --write  # write _build/QUERY-TABLE.md
"""
from __future__ import annotations

import argparse
import html
import pathlib
import re
import sys

SITE = pathlib.Path(__file__).resolve().parent.parent

#: Search Console, 2026-09-07. The only impressions we actually have.
KNOWN = {
    "/learn/ad-copy-truncation-vs-hard-limits/": [
        ("bing ads character limits", 50), ("bing ad character limit", 32),
        ("meta headline character limit", 5), ("meta ad copy character limit", 5),
        ("linkedin ad copy character limits", 4), ("tiktok character limit ads", 3)],
    "/learn/audience-floors-by-platform/": [
        ("minimum audience size for linkedin ads", 15)],
}
PAGE_IMPRESSIONS = {
    "/learn/ad-copy-truncation-vs-hard-limits/": 297,
    "/learn/audience-floors-by-platform/": 52,
    "/specs/": 46,
    "/learn/meta-lookalike-minimum-source/": 35,
    "/learn/special-ad-categories/": 30,
    "/learn/linkedin-ad-set-not-delivering/": 22,
}

HAS_NUMBER = re.compile(r"\$\s?\d|\b\d+%|\b\d{2,}\b|\b\d{1,3}(?:,\d{3})+\b")
ATTRIBUTED = re.compile(
    r"\b(?:since|established|founded|licen[cs]ed|certified|insured|guarantee|"
    r"warranty|years of experience|according to"
    r"|we (?:measured|surveyed|tested|analysed|analyzed|counted|sampled|read)"
    r"|our (?:research|data|study|survey|testing|analysis|sample|measurement)"
    r"|n\s*=\s*\d+|sample of \d+|median|average of)", re.I)

#: A title somebody would TYPE contains a thing and a question-ish shape.
#: Deliberately crude, and it is the one column a human should overrule.
QUERY_SHAPED = re.compile(
    r"\b(?:limits?|size|minimum|maximum|how|why|what|which|when|vs|versus"
    r"|cost|price|specs?|requirements?|rules?|not delivering|error)\b", re.I)


def _prose(p: pathlib.Path) -> tuple[str, str, str]:
    raw = p.read_text(errors="replace")
    title = (re.search(r"<title>([^<]*)", raw) or [None, ""])[1].split("|")[0].strip()
    raw = re.sub(r"<(script|style)\b.*?</\1>", " ", raw, flags=re.S | re.I)
    art = re.search(r"<article[^>]*>(.*?)</article>", raw, re.S)
    body = art.group(1) if art else raw
    # The lede is what an answer engine reads first.
    lede = re.sub(r"<[^>]+>", " ", body)
    lede = html.unescape(re.sub(r"\s+", " ", lede)).strip()
    return title, lede[:300], lede


def rows() -> list:
    out = []
    for f in sorted(SITE.glob("**/index.html")):
        if ".git" in str(f):
            continue
        url = "/" + str(f.parent.relative_to(SITE)).replace(".", "").strip("/")
        url = "/" if url == "/" else url.rstrip("/") + "/"
        title, opening, full = _prose(f)
        if len(full) < 400:            # hubs and stubs answer nothing on their own
            continue
        queries = KNOWN.get(url, [])
        out.append({
            "url": url,
            "impressions": PAGE_IMPRESSIONS.get(url, 0),
            "title": title,
            "queries": queries,
            "query_shaped": bool(QUERY_SHAPED.search(title)),
            # Does the opening answer, or does it warm up first?
            "answers_early": bool(HAS_NUMBER.search(opening)),
            "sourced": bool(HAS_NUMBER.search(full)) and bool(ATTRIBUTED.search(full)),
        })
    return sorted(out, key=lambda r: (-r["impressions"], r["url"]))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    rs = rows()
    lines = [
        "# What query is each page's title?",
        "",
        "Generated by `_build/query_table.py`. Search Console data 2026-09-07:",
        "558 impressions, 0 clicks, average position 66.",
        "",
        "**This cannot see a SERP.** The order asks whether each body answers its",
        "query *better than the page currently ranking*; nothing on this machine",
        "can know that, and a column claiming it would be invented. The columns",
        "below are what is measurable here.",
        "",
        "| impr | page | title reads as a query | answers in the first 300 chars | number + source |",
        "|---:|---|:--:|:--:|:--:|",
    ]
    tick = {True: "yes", False: "**no**"}
    for r in rs:
        lines.append(
            f"| {r['impressions'] or ''} | `{r['url']}` | {tick[r['query_shaped']]} "
            f"| {tick[r['answers_early']]} | {tick[r['sourced']]} |")

    weak = [r for r in rs if not r["query_shaped"]]
    late = [r for r in rs if r["query_shaped"] and not r["answers_early"]]
    lines += ["", "## Pages whose title names no query", ""]
    lines += [f"- `{r['url']}` — {r['title']!r}" for r in weak] or ["- none"]
    lines += ["", "## Query-shaped, but the answer is not in the opening", ""]
    lines += [f"- `{r['url']}`" for r in late] or ["- none"]
    lines += ["", "## Queries we actually earn impressions for", ""]
    for url, qs in KNOWN.items():
        for q, n in qs:
            lines.append(f"- {n:>3} · {q!r} → `{url}`")

    text = "\n".join(lines) + "\n"
    if args.write:
        (SITE / "_build" / "QUERY-TABLE.md").write_text(text)
        print(f"wrote _build/QUERY-TABLE.md — {len(rs)} pages, "
              f"{len(weak)} with no query in the title, "
              f"{len(late)} answering late")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
