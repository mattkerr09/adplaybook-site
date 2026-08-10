#!/usr/bin/env python3
"""Build adplaybook.app from the product's own data.

The whole SEO thesis of this site is one observation: **the pages currently
ranking for ad-spec queries are wrong.** A page ranking today for LinkedIn's
limits states the introductory text maxes at 600 characters; LinkedIn's own
help centre says 3,000, with 150 to avoid truncation. Another states TikTok
caps ad captions at 100 characters; TikTok's own in-feed specification page
states no character count at all. Both were checked against the platforms'
documentation on 2026-08-10.

Undated, uncited and incorrect is what page one looks like. So this site's
pages carry, for every number: the platform's own words, the URL they came
from, and the date they were read — plus an explicit list of what could *not*
be verified, because a spec sheet with no gaps is either complete or lying and
the reader cannot tell which.

They are generated straight from `backend/adkit/platforms/*.json` — the same
files the app itself reads. That is deliberate: the site cannot drift from the
product, and when the daily spec-diff job updates a limit, the page changes
with it. A marketing site maintained separately from the thing it describes
goes stale in a month and nobody notices.

    python _build/render.py [--app-repo PATH]
"""

from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import sys
from datetime import date
from pathlib import Path
from typing import Any, Dict, List

SITE = Path(__file__).resolve().parents[1]
BASE_URL = "https://adplaybook.app"
BUILT = date.today().isoformat()

BRAND = "AdPlaybook"
TAGLINE = "The ad maker that knows which strategy fits — and proves every claim."


# ---------------------------------------------------------------------------
# Page shell
# ---------------------------------------------------------------------------

CSS = """
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#0d1017;--surface:#141822;--surface-2:#1b2130;--line:#242c3b;
  --ink:#e8ecf4;--ink-mid:#a3adc0;--ink-dim:#6f7a8d;
  --accent:#4c8dff;--accent-light:#7fb0ff;--accent-ink:#0d1420;
  --ok:#4fae7a;--warn:#d9a72b;--bad:#d9554f;
  --sans:-apple-system,BlinkMacSystemFont,"Segoe UI",Inter,system-ui,sans-serif;
  --mono:ui-monospace,SFMono-Regular,"SF Mono",Menlo,monospace;
}
@media (prefers-color-scheme:light){:root{
  --bg:#f7f9fc;--surface:#fff;--surface-2:#eef2f8;--line:#dde4ee;
  --ink:#131722;--ink-mid:#4d5768;--ink-dim:#7b8598;--accent:#1d5fd1;--accent-light:#164aa6;--accent-ink:#fff;
}}
html{scroll-behavior:smooth}
body{background:var(--bg);color:var(--ink);font-family:var(--sans);font-size:17px;line-height:1.65;-webkit-font-smoothing:antialiased}
a{color:var(--accent-light);text-decoration:none}
a:hover{text-decoration:underline}
.wrap{width:min(820px,calc(100% - 2rem));margin:0 auto}
nav{position:sticky;top:0;z-index:10;background:color-mix(in srgb,var(--bg) 92%,transparent);backdrop-filter:blur(12px);border-bottom:1px solid var(--line)}
.nav-inner{display:flex;align-items:center;justify-content:space-between;height:60px;gap:1rem}
.nav-brand{display:flex;align-items:center;gap:.55rem;font-weight:700;color:var(--ink);font-size:1.05rem}
.nav-brand:hover{text-decoration:none;color:var(--accent-light)}
.nav-logo{width:26px;height:26px;border-radius:6px;display:block}
.nav-links{display:flex;gap:1.1rem;list-style:none;font-size:.92rem;flex-wrap:wrap}
.nav-links a{color:var(--ink-mid)}
.nav-links a:hover{color:var(--ink);text-decoration:none}
article,main{padding:2.6rem 0 4rem}
.crumb{font-family:var(--mono);font-size:.76rem;color:var(--ink-dim);text-transform:uppercase;letter-spacing:.08em;margin-bottom:.9rem}
h1{font-size:2.1rem;line-height:1.2;letter-spacing:-.02em;margin-bottom:.8rem}
h2{font-size:1.4rem;line-height:1.3;margin:2.4rem 0 .8rem;letter-spacing:-.01em}
h3{font-size:1.1rem;margin:1.6rem 0 .5rem}
p{margin:0 0 1rem}
.lede{font-size:1.15rem;color:var(--ink-mid);margin-bottom:1.6rem}
ul,ol{margin:0 0 1rem 1.25rem}
li{margin-bottom:.4rem}
code{font-family:var(--mono);font-size:.88em;background:var(--surface-2);padding:.12em .38em;border-radius:4px}
table{width:100%;border-collapse:collapse;margin:1.2rem 0;font-size:.94rem;display:block;overflow-x:auto}
th,td{text-align:left;padding:.6rem .7rem;border-bottom:1px solid var(--line);vertical-align:top}
th{font-size:.8rem;text-transform:uppercase;letter-spacing:.05em;color:var(--ink-dim);font-weight:600}
blockquote{border-left:3px solid var(--accent);padding:.2rem 0 .2rem 1rem;margin:1rem 0;color:var(--ink-mid)}
.panel{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:1.1rem 1.2rem;margin:1.4rem 0}
.panel.warn{border-left:3px solid var(--warn)}
.panel.ok{border-left:3px solid var(--ok)}
.src{font-size:.85rem;color:var(--ink-dim);font-family:var(--mono);word-break:break-all}
.pill{display:inline-block;font-family:var(--mono);font-size:.72rem;padding:.16rem .5rem;border-radius:999px;border:1px solid var(--line);color:var(--ink-dim);margin-right:.3rem}
.pill.checked{border-color:var(--ok);color:var(--ok)}
.pill.unchecked{border-color:var(--warn);color:var(--warn)}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:.9rem;margin:1.4rem 0}
.card{display:block;background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:1rem;color:var(--ink)}
.card:hover{border-color:var(--accent);text-decoration:none}
.card strong{display:block;margin-bottom:.25rem}
.card span{font-size:.88rem;color:var(--ink-dim)}
.cta{display:inline-block;background:var(--accent);color:var(--accent-ink);font-weight:600;padding:.7rem 1.3rem;border-radius:8px;margin:.4rem .5rem .4rem 0}
.cta:hover{text-decoration:none;opacity:.92}
.cta.ghost{background:transparent;color:var(--ink);border:1px solid var(--line)}
footer{border-top:1px solid var(--line);padding:2rem 0 3rem;color:var(--ink-dim);font-size:.9rem}
footer a{color:var(--ink-mid)}
.hero{padding:3.4rem 0 1rem}
.hero h1{font-size:2.6rem}
@media(max-width:640px){.hero h1{font-size:2rem}h1{font-size:1.7rem}body{font-size:16px}}
"""

LOGO_SVG = (
    '<svg class="nav-logo" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">'
    '<rect width="100" height="100" rx="22" fill="#141822"/>'
    '<rect x="14" y="14" width="14" height="72" rx="4" fill="#4c8dff"/>'
    '<rect x="33" y="14" width="53" height="72" rx="6" fill="#4c8dff"/>'
    '<circle cx="46" cy="70" r="9.5" fill="#141822"/><circle cx="46" cy="70" r="4.3" fill="#4c8dff"/>'
    '<circle cx="61" cy="53" r="5" fill="#141822"/><circle cx="75" cy="36" r="5" fill="#141822"/>'
    "</svg>"
)

NAV = [("/specs/", "Ad specs"), ("/learn/", "Learn"), ("/vs/", "Compare"), ("/#get", "Get it")]


def esc(s: Any) -> str:
    return html.escape(str(s), quote=True)


def page(*, path: str, title: str, description: str, body: str,
         schema: Dict[str, Any] | None = None, modified: str = BUILT) -> None:
    """Write one page. `path` is the URL path, e.g. /specs/linkedin/."""
    url = BASE_URL + path
    nav = "".join(f'<li><a href="{h}">{esc(t)}</a></li>' for h, t in NAV)
    ld = ""
    if schema:
        ld = ('<script type="application/ld+json">'
              + json.dumps(schema, separators=(",", ":")) + "</script>")

    doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<meta name="theme-color" content="#0d1017">
<meta name="last-modified" content="{modified}">
<link rel="canonical" href="{url}">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<meta property="og:type" content="{'website' if path == '/' else 'article'}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:url" content="{url}">
<meta property="og:site_name" content="{BRAND}">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(description)}">
<style>{CSS}</style>
{ld}
</head>
<body>
<nav><div class="wrap nav-inner">
<a class="nav-brand" href="/">{LOGO_SVG}{BRAND}</a>
<ul class="nav-links">{nav}</ul>
</div></nav>
<div class="wrap">{body}</div>
<footer><div class="wrap">
<p><strong>{BRAND}</strong> — {esc(TAGLINE)}</p>
<p>Every figure on this site is quoted from the platform's own documentation with
the date it was read. Where something could not be verified, the page says so
rather than leaving a gap you cannot see.</p>
<p><a href="/specs/">Ad specs</a> · <a href="/learn/">Learn</a> ·
<a href="/vs/">Compare</a> · <a href="/llms.txt">llms.txt</a></p>
</div></footer>
</body>
</html>
"""
    out = SITE / path.strip("/") / "index.html" if path != "/" else SITE / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(doc)
    PAGES.append((path, modified))


PAGES: List[tuple] = []


# ---------------------------------------------------------------------------
# Platform spec pages — the reason this site can win
# ---------------------------------------------------------------------------

def _fmt_limit(pl: Dict[str, Any], stem: str) -> str:
    safe, hard = pl.get(f"{stem}_chars"), pl.get(f"{stem}_max_chars")
    if safe and hard and safe != hard:
        return f"<strong>{safe}</strong> to stay visible · {hard} hard cap"
    if safe:
        return f"<strong>{safe}</strong>"
    if hard:
        return f"<strong>{hard}</strong>"
    return '<span class="pill unchecked">not stated</span>'


def spec_page(spec: Dict[str, Any]) -> None:
    key, name = spec["key"], spec["name"]
    manager = spec.get("manager_name", name)
    placements = spec.get("placements", [])
    checked = [p for p in placements if p.get("verified_on")]
    read_on = max((p["verified_on"] for p in checked), default=None)

    rows = []
    for p in placements:
        rows.append(
            f"<tr><td><strong>{esc(p.get('name', p['key']))}</strong><br>"
            f"<span class='src'>{esc(p.get('aspect_ratio', ''))} "
            f"{esc(p.get('recommended_resolution', ''))}</span></td>"
            f"<td>{_fmt_limit(p, 'headline')}</td>"
            f"<td>{_fmt_limit(p, 'primary_text')}</td>"
            f"<td>{esc(p.get('max_file_size_mb', '—'))}"
            f"{' MB' if p.get('max_file_size_mb') else ''}</td></tr>"
        )

    notes = []
    for p in placements:
        for stem, label in (("headline", "Headline"), ("primary_text", "Body text"),
                            ("description", "Description")):
            n = p.get(f"{stem}_note")
            if n and '"' in n:
                notes.append(f"<h3>{esc(p.get('name', p['key']))} — {label}</h3>"
                             f"<blockquote>{esc(n)}</blockquote>")

    unverified = spec.get("_unverified", [])
    unv_html = ""
    if unverified:
        items = "".join(f"<li>{esc(u)}</li>" for u in unverified)
        unv_html = (
            '<div class="panel warn"><strong>What we could not verify</strong>'
            f"<ul>{items}</ul>"
            "<p>Listed rather than omitted. A spec sheet with no gaps is either "
            "complete or hiding something, and from the outside those look "
            "identical.</p></div>"
        )

    caveat = spec.get("_experiment_caveat", "")
    # The heading is derived from the platform's own numbers rather than being
    # one shared string. Seven spec pages with an identical H2 skeleton is what
    # a thin-content penalty is actually measuring — the pages differ in
    # substance, so they should differ in shape.
    caveat_head = {
        "linkedin": "Small audiences and the cost of splitting them",
        "tiktok":   "Why an ad group here refuses to spend",
        "youtube":  "Decide the video length before anything else",
        "pinterest": "The description nobody reads",
        "x":        "A link costs you 23 characters",
        "reddit":   "The comment thread is part of the ad",
        "google":   "Responsive ads recombine before anyone sees them",
        "meta":     "What the learning phase does to a test",
    }.get(key, "What breaks a campaign here")
    caveat_html = (f"<h2>{esc(caveat_head)}</h2><p>{esc(caveat)}</p>"
                   if caveat else "")

    targeting = spec.get("targeting_capabilities", {}) or {}
    floors = []
    for k, v in targeting.items():
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            note = targeting.get(f"{k}_note", "")
            floors.append(f"<li><strong>{esc(k.replace('_', ' '))}: {v}</strong> — {esc(note)}</li>")
    floor_label = {
        "linkedin": "The 300-account floor, per ad set",
        "tiktok": "The 1,000 matched-user floor",
        "youtube": "The 10 and 12 second thresholds",
    }.get(key, "Hard floors")
    floor_html = (f'<div class="panel"><strong>{esc(floor_label)}</strong><ul>{"".join(floors)}</ul>'
                  "<p>These are the numbers that decide whether a campaign delivers "
                  "at all, and none of them produce an error message when you cross "
                  "them.</p></div>" if floors else "")

    src = spec.get("source_url", "")
    check_head = ("Count these before you paste" if placements and any(
        p.get("headline_chars") or p.get("primary_text_chars") for p in placements)
        else "Check a campaign against this spec")
    title = f"{name} ad specs and character limits ({BUILT[:4]}) | {BRAND}"
    desc = (f"{name} ad character limits, image sizes and hard floors — every "
            f"figure quoted from {name}'s own documentation with the date it was read"
            + (f", {read_on}." if read_on else "."))

    body = f"""
<article>
<p class="crumb"><a href="/specs/">Ad specs</a> / {esc(name)}</p>
<h1>{esc(name)} ad specs and character limits</h1>
<p class="lede">{esc(desc)}</p>

<div class="panel ok">
<p style="margin:0"><span class="pill checked">read {esc(read_on or 'unverified')}</span>
Source: <a class="src" href="{esc(src)}" rel="nofollow noopener">{esc(src)}</a></p>
</div>

<h2>Character limits and sizes</h2>
<table><thead><tr><th>Placement</th><th>Headline</th><th>Body text</th><th>Max file</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table>
<p>Where two numbers are given, the first is what stays visible and the second
is what the field accepts. They are different questions: copy over the cap is
rejected at upload, copy over the visible limit runs and gets cut off. Most
guides publish only one of the two.</p>

{floor_html}
{''.join(notes[:6])}
{caveat_html}
{unv_html}

<h2>{check_head}</h2>
<p>{BRAND} holds this spec as dated data and checks a finished campaign against
it — character counts, audience floors, forbidden exclusions — before you paste
anything into {esc(manager)}. It is arithmetic, not a judgement call, so it runs
on every campaign and costs nothing.</p>
<p><a class="cta" href="/#get">Get {BRAND}</a>
<a class="cta ghost" href="/specs/">All eight platforms</a></p>
</article>
"""
    page(path=f"/specs/{key}/", title=title, description=desc, body=body,
         modified=read_on or BUILT,
         schema={
             "@context": "https://schema.org", "@type": "TechArticle",
             "headline": f"{name} ad specs and character limits",
             "description": desc, "datePublished": read_on or BUILT,
             "dateModified": read_on or BUILT,
             "publisher": {"@type": "Organization", "name": BRAND},
             "isBasedOn": src,
         })


def load_specs(app_repo: Path) -> List[Dict[str, Any]]:
    d = app_repo / "backend" / "adkit" / "platforms"
    if not d.is_dir():
        sys.exit(f"platform specs not found at {d} — pass --app-repo")
    out = []
    for f in sorted(d.glob("*.json")):
        spec = json.loads(f.read_text())
        # Recompute the unverified list the same way the app does, so the page
        # and the product can never disagree about what was checked.
        unv = []
        for p in spec.get("placements", []):
            if not p.get("verified_on"):
                unv.append(f"The limits for {p.get('name', p['key'])} were never "
                           "checked against the platform's own documentation.")
        if not spec.get("cta_buttons_verified_on"):
            unv.append("Which call-to-action buttons this platform offers.")
        if not (spec.get("special_ad_categories") or {}).get("verified_on"):
            unv.append("Which ad categories are restricted here, and what "
                       "declaring one does to your targeting.")
        if not (spec.get("measurement") or {}).get("verified_on"):
            unv.append("How this platform tracks conversions, and its default "
                       "attribution window.")
        spec["_unverified"] = unv
        out.append(spec)
    return out


def specs_hub(specs: List[Dict[str, Any]]) -> None:
    cards = "".join(
        f'<a class="card" href="/specs/{s["key"]}/"><strong>{esc(s["name"])}</strong>'
        f'<span>{len(s.get("placements", []))} placement(s) · '
        f'{len(s["_unverified"])} thing(s) unverified</span></a>'
        for s in specs
    )
    body = f"""
<article>
<p class="crumb">Ad specs</p>
<h1>Ad specs and character limits, with sources</h1>
<p class="lede">Eight platforms. Every number quoted from the platform's own
documentation, with the URL it came from and the date it was read.</p>

<div class="panel warn">
<strong>Why this page exists</strong>
<p>The guides ranking for these queries are frequently wrong, and none of them
show their working. Two examples found while building this, both checked
against the platforms' own help centres on 2026-08-10:</p>
<ul>
<li>A widely-ranked page states LinkedIn's introductory text maxes out at 600
characters. LinkedIn's own help centre says <strong>3,000</strong>, with 150 to
avoid truncation.</li>
<li>Several pages state TikTok caps ad captions at 100 characters. TikTok's own
in-feed specification page states <strong>no character count at all</strong>.
The figure appears nowhere in their documentation.</li>
</ul>
<p>Undated and uncited is the norm. So every figure here carries its source and
its date, and anything that could not be read is listed as unverified rather
than quietly skipped.</p>
</div>

<div class="grid">{cards}</div>

<h2>Where these come from</h2>
<p>These pages are generated from the same files {BRAND} itself reads when it
builds a campaign, so the site cannot drift from the product. When a platform
changes a limit and the spec is re-checked, the page changes with it.</p>
<p><a class="cta" href="/#get">Get {BRAND}</a></p>
</article>
"""
    page(path="/specs/", title=f"Ad specs and character limits for 8 platforms | {BRAND}",
         description=("Ad character limits, image sizes and hard floors for Meta, Google, "
                      "LinkedIn, TikTok, X, Pinterest, Reddit and YouTube — every figure "
                      "quoted from the platform's own documentation with the date read."),
         body=body)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--app-repo", default=str(Path.home() / "ad maker app"))
    args = ap.parse_args()

    specs = load_specs(Path(args.app_repo))
    specs_hub(specs)
    for s in specs:
        spec_page(s)

    from content import build_rest  # noqa: E402
    build_rest(page, specs, PAGES)

    # sitemap
    urls = "".join(
        f"<url><loc>{BASE_URL}{p}</loc><lastmod>{m}</lastmod></url>"
        for p, m in sorted(set(PAGES))
    )
    (SITE / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        f"{urls}</urlset>\n")

    print(f"built {len(PAGES)} pages")
    for p, _ in sorted(set(PAGES)):
        print(f"  {p}")
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    raise SystemExit(main())
