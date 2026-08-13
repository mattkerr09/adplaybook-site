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


def check_referenced_assets(pages: list, fails: list[str]) -> None:
    """Absolute URLs must be URLs, and referenced local assets must exist.

    Added because a real bug got through: og:image was rendered from `SITE`,
    which in render.py is a filesystem Path, so every page shipped
    `content="/Users/matthewkerr/adplaybook-site/og.png"`. The page validated,
    the build was clean, and the card would simply not have loaded anywhere.

    Two things a program can settle, so it should:
      * a src/href/content that looks like a local absolute path is never right
      * a same-origin asset referenced by a page has to exist on disk
    """
    for p in pages:
        raw = p.read_text()
        rel = "/" + str(p.relative_to(SITE)).replace("index.html", "")

        for m in re.finditer(r'(?:content|href|src)="(/Users/|/home/|file://|[A-Za-z]:\\\\)[^"]*"', raw):
            fails.append(f"{rel}: a filesystem path published as a URL - {m.group(0)[:90]}")

        for m in re.finditer(r'(?:content|href|src)="https://adplaybook\.app(/[^"]*)"', raw):
            target = m.group(1)
            if target.endswith("/") or "#" in target:
                continue
            if not (SITE / target.lstrip("/")).exists():
                fails.append(f"{rel}: references {target}, which does not exist on disk")

        for m in re.finditer(r'(?:src|href)="(/[^/"][^"]*\.(?:png|jpg|jpeg|webp|svg|css|js|pdf))"', raw):
            target = m.group(1)
            if not (SITE / target.lstrip("/")).exists():
                fails.append(f"{rel}: references {target}, which does not exist on disk")


def check_download_link(pages, fails, warns) -> None:
    """The download button is an instruction. Run it before publishing it.

    The site has offered v0.1.5 since it went up. That build cannot complete a
    single campaign — it calls Client() where the pipeline expects a Provider,
    so every run dies with a TypeError before producing anything. Eighteen
    later builds are signed, notarised and stapled on the developer's disk, and
    a visitor downloading right now still gets the one that does not work.

    Nothing here noticed, because nothing here looked. This looks.

    Two separate checks, because they fail differently:

      * the URL must resolve. A version bump with no matching release turns the
        primary call to action into a 404, which is worse than stale.
      * the version must not trail the app's own releases. Silent staleness is
        how five months of shipping ends up invisible to everybody but the
        person doing it.

    Network access is required, so a failure to reach GitHub is reported as
    unchecked rather than as a pass. A gate that cannot see something has to
    say so — treating "no answer" as "fine" is how this got missed.
    """
    import re
    import urllib.error
    import urllib.request

    urls = set()
    for p in pages:
        urls.update(re.findall(r'https://[^"\s]+\.dmg', p.read_text()))
    if not urls:
        fails.append("no download link anywhere on the site")
        return

    for url in sorted(urls):
        m = re.search(r"/v?(\d+\.\d+\.\d+)/", url)
        shown = m.group(1) if m else "?"
        req = urllib.request.Request(url, method="HEAD")
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                if r.status >= 400:
                    fails.append(f"download link returns {r.status}: {url}")
                    continue
        except urllib.error.HTTPError as exc:
            fails.append(
                f"download link returns {exc.code}: {url} — the primary call "
                "to action on this site is broken")
            continue
        except Exception as exc:  # noqa: BLE001
            warns.append(
                f"could not check the download link ({exc}). NOT verified — "
                "this is unchecked, not clean.")
            continue

        # Does a newer build exist that nobody can download?
        # Sorted as VERSIONS, not as filenames. The first draft of this sorted
        # the .dmg names as strings and reported 0.1.9 as the newest build
        # while 0.1.23 sat beside it — "0.1.9" > "0.1.23" lexicographically.
        # A gate that publishes a wrong number is the thing it exists to catch.
        found = []
        for q in (pathlib.Path.home() / "ad maker app" / "dist").glob("*.dmg"):
            m2 = re.search(r"(\d+\.\d+\.\d+)", q.name)
            if m2:
                found.append(_ver(m2.group(1)))
        if found and max(found) > _ver(shown):
            newest = ".".join(str(x) for x in max(found))
            warns.append(
                f"the site offers {shown} but {newest} is built and signed. "
                "Every visitor is downloading a version the developer has "
                "already replaced.")

        # A PUBLISHED release the site does not link is a different animal, and
        # it fails rather than warns.
        #
        # A build sitting in dist/ is work in progress — source runs ahead of the
        # download all day and a gate that fires on that would be red constantly,
        # which is how a gate teaches people to ignore it. Publishing a release is
        # a deliberate act that means "this is the one people should get". If the
        # site then does not point at it, the release is unreachable and the
        # publish silently did nothing.
        #
        # That is not hypothetical: v0.1.23 was published at 00:18 on 2026-08-13
        # and adplaybook.app still served v0.1.5 — a build that could not complete
        # a single campaign — for nearly two hours afterwards. The warning above
        # was firing the whole time and blocked nothing.
        latest = _latest_release()
        if latest is None:
            warns.append(
                "could not reach the releases API. The published-release check "
                "did NOT run — this is unchecked, not clean.")
        elif _ver(latest) > _ver(shown):
            fails.append(
                f"the site offers {shown} but {latest} is PUBLISHED. A release "
                "nobody can download from the site is a release that did not "
                "happen — point the download at it or unpublish it.")


def _latest_release():
    """Newest published release tag, or None if GitHub could not be reached.

    None means unknown, never 'fine'. The caller reports it as unchecked.
    """
    import json
    import urllib.error
    import urllib.request

    url = ("https://api.github.com/repos/mattkerr09/adplaybook-site/"
           "releases/latest")
    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": "adplaybook-site-check/1.0",
                          "Accept": "application/vnd.github+json"})
        with urllib.request.urlopen(req, timeout=20) as r:
            tag = json.load(r).get("tag_name") or ""
    except Exception:  # noqa: BLE001 — any failure means "unknown"
        return None
    m = re.search(r"(\d+\.\d+\.\d+)", tag)
    return m.group(1) if m else None


def _ver(s: str):
    return tuple(int(x) for x in s.split("."))


def main() -> int:
    pages = sorted(SITE.glob("**/index.html"))
    if not pages:
        print("no pages built"); return 1

    fails: list[str] = []
    warns: list[str] = []

    check_referenced_assets(pages, fails)
    check_download_link(pages, fails, warns)

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
