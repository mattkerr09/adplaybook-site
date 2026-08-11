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
/* Design tokens match the sibling products on purpose — same black, same
   hairlines, same pill buttons — with this app's blue in place of Crisp's
   cyan. A family of tools that look unrelated reads as three hobby projects. */
:root{
  --black:#000;--panel:#08090d;--panel-2:#0d0f15;--card:#101319;
  --hair:#1c2029;--hair-lit:#2a3040;
  --white:#f5f7fa;--grey:#a1a9b8;--grey-dim:#6b7382;
  --blue:#4c8dff;--ice:#a8c8ff;--violet:#9d8cff;--green:#4ade80;--amber:#d9a72b;
  --r:18px;--r-sm:12px;
  --sans:-apple-system,BlinkMacSystemFont,"SF Pro Display","Segoe UI",Inter,system-ui,sans-serif;
  --mono:ui-monospace,SFMono-Regular,"SF Mono",Menlo,monospace;
  --w:1080px;--wr:820px;
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%;scroll-behavior:smooth}
body{margin:0;background:var(--black);color:var(--white);font-family:var(--sans);
  font-size:17px;line-height:1.7;-webkit-font-smoothing:antialiased;overflow-x:hidden}
img,svg{max-width:100%}
a{color:var(--ice);text-decoration:none}
a:hover{text-decoration:underline;text-underline-offset:3px}
.wrap{width:min(var(--wr),calc(100% - 2.6rem));margin:0 auto}
.wide{width:min(var(--w),calc(100% - 2.6rem));margin:0 auto}

nav{position:sticky;top:0;z-index:80;background:rgba(0,0,0,.6);
  backdrop-filter:saturate(180%) blur(20px);-webkit-backdrop-filter:saturate(180%) blur(20px);
  border-bottom:1px solid rgba(28,32,41,.9)}
.nav-inner{display:flex;align-items:center;gap:1.5rem;height:58px;
  width:min(var(--w),calc(100% - 2.6rem));margin:0 auto}
.nav-brand{display:flex;align-items:center;gap:.55rem;color:var(--white);font-weight:640;
  font-size:1.02rem;letter-spacing:-.015em}
.nav-brand:hover{text-decoration:none}
.nav-logo{width:22px;height:22px;display:block}
.nav-links{display:flex;gap:1.35rem;list-style:none;margin:0;padding:0;font-size:.9rem;
  margin-left:auto;align-items:center}
.nav-links a{color:var(--grey)}
.nav-links a:hover{color:var(--white);text-decoration:none}
.nav-links .btn{padding:.48rem 1.05rem;font-size:.87rem;color:#02101f}
/* .nav-links a sets grey; the button needs its own colour back or the label
   disappears into the gradient it sits on. */
.nav-links .btn:hover{color:#02101f}
.nav-links .btn svg{flex:none}

h1{font-size:clamp(2.1rem,4.6vw,3.2rem);line-height:1.06;letter-spacing:-.035em;
  font-weight:690;margin:.6rem 0 1rem}
h2{font-size:clamp(1.45rem,2.7vw,2rem);line-height:1.18;letter-spacing:-.028em;
  font-weight:660;margin:3.2rem 0 .9rem}
h3{font-size:1.12rem;font-weight:640;letter-spacing:-.012em;margin:2rem 0 .5rem}
p{margin:0 0 1.05rem}
ul,ol{margin:0 0 1.15rem 1.2rem;padding:0}
li{margin-bottom:.5rem}
.grad{background:linear-gradient(105deg,#cfe0ff 0%,#4c8dff 44%,#9d8cff 100%);
  -webkit-background-clip:text;background-clip:text;color:transparent}
.lede{font-size:clamp(1.05rem,1.6vw,1.2rem);line-height:1.55;color:var(--grey);margin:0 0 1.6rem}
.muted{color:var(--grey)}
.crumb{font-size:.85rem;color:var(--grey-dim);margin:2.2rem 0 .4rem;font-family:var(--mono)}
.crumb a{color:var(--grey)}

.btn{display:inline-flex;align-items:center;justify-content:center;gap:.55rem;
  padding:.78rem 1.4rem;border-radius:999px;font-weight:600;font-size:.96rem;
  background:linear-gradient(180deg,#7aaeff,#3272ea);color:#02101f;border:1px solid transparent;
  box-shadow:0 10px 34px -12px rgba(76,141,255,.85);
  transition:transform .2s cubic-bezier(.2,.8,.2,1),box-shadow .25s}
.btn:hover{transform:translateY(-2px);box-shadow:0 16px 44px -12px rgba(76,141,255,1);
  text-decoration:none}
.btn.ghost{background:transparent;color:var(--white);border:1px solid var(--hair-lit);
  box-shadow:none}
.btn.ghost:hover{border-color:var(--blue);box-shadow:none}

.hero{position:relative;text-align:center;padding:5rem 0 3.4rem}
.hero::before{content:"";position:absolute;inset:-30% -50% auto;height:120%;pointer-events:none;
  background:radial-gradient(760px 420px at 50% 0,rgba(76,141,255,.16),transparent 70%)}
.hero>*{position:relative}
.hero h1{font-size:clamp(2.6rem,7vw,4.6rem);margin:.9rem 0 1.2rem}
.hero .lede{max-width:62ch;margin-inline:auto}
.eyebrow{display:inline-flex;align-items:center;gap:.5rem;padding:.4rem 1rem;border-radius:999px;
  border:1px solid var(--hair-lit);background:var(--panel-2);color:var(--ice);
  font-size:.86rem;font-weight:560;white-space:nowrap}
/* An inline SVG with no intrinsic size fills its flex line. Without this the
   eyebrow tick rendered about 120px tall and pushed the label onto three
   lines. Every icon in this stylesheet gets an explicit box. */
.eyebrow svg{width:14px;height:14px;flex:none;color:var(--green)}
.hero-actions{display:flex;gap:.8rem;justify-content:center;flex-wrap:wrap;margin:2rem 0 1rem}
.hero-sub{font-size:.88rem;color:var(--grey-dim);font-family:var(--mono)}
.trust{display:flex;gap:1.6rem;justify-content:center;flex-wrap:wrap;margin-top:2.4rem;
  font-size:.9rem;color:var(--grey)}
.trust span{display:inline-flex;align-items:center;gap:.45rem}
.trust svg{width:15px;height:15px;color:var(--green);flex:none}

section{padding:1rem 0}
.kicker{font-family:var(--mono);font-size:.76rem;letter-spacing:.1em;text-transform:uppercase;
  color:var(--blue);margin-bottom:.5rem}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:1rem;margin:1.6rem 0}
.card{display:block;padding:1.3rem 1.4rem;border:1px solid var(--hair);border-radius:var(--r);
  background:linear-gradient(180deg,var(--card),var(--panel-2));color:var(--white);
  transition:border-color .2s,transform .2s}
.card:hover{border-color:var(--hair-lit);transform:translateY(-2px);text-decoration:none}
.card strong{display:block;margin-bottom:.3rem;font-weight:640;letter-spacing:-.01em}
.card span{font-size:.9rem;color:var(--grey);line-height:1.55}
.card .num{font-family:var(--mono);font-size:2rem;font-weight:600;color:var(--blue);
  line-height:1;display:block;margin-bottom:.5rem}

.box{margin:2rem 0;padding:1.35rem 1.5rem;border:1px solid var(--hair);border-radius:var(--r-sm);
  background:var(--panel-2);color:var(--grey)}
.box strong{color:var(--white)}
.box p:last-child{margin-bottom:0}
.box.warn{border-left:3px solid var(--amber)}
.box.ok{border-left:3px solid var(--green)}

.cta-block{margin:3.4rem 0 1rem;padding:2.4rem 2rem;border:1px solid var(--hair);
  border-radius:var(--r);text-align:center;
  background:radial-gradient(600px 300px at 20% -20%,rgba(76,141,255,.13),transparent 70%),
    linear-gradient(180deg,var(--card),var(--panel-2))}
.cta-block p{color:var(--grey)}

table{width:100%;border-collapse:collapse;margin:1.4rem 0;font-size:.94rem;display:block;
  overflow-x:auto;white-space:nowrap}
th,td{text-align:left;padding:.72rem .8rem;border-bottom:1px solid var(--hair);vertical-align:top;
  white-space:normal}
th{font-size:.74rem;text-transform:uppercase;letter-spacing:.07em;color:var(--grey-dim);
  font-weight:600}
td strong{font-weight:640}
tbody tr:hover{background:rgba(255,255,255,.02)}
blockquote{border-left:2px solid var(--blue);padding:.1rem 0 .1rem 1.1rem;margin:1.1rem 0;
  color:var(--grey);font-style:normal}
code{font-family:var(--mono);font-size:.88em;background:var(--panel-2);padding:.14em .4em;
  border-radius:6px;border:1px solid var(--hair)}
.src{font-size:.84rem;color:var(--grey-dim);font-family:var(--mono);word-break:break-all}
.pill{display:inline-block;font-family:var(--mono);font-size:.72rem;padding:.18rem .6rem;
  border-radius:999px;border:1px solid var(--hair-lit);color:var(--grey-dim);margin-right:.35rem}
.pill.checked{border-color:rgba(74,222,128,.5);color:var(--green)}
.pill.unchecked{border-color:rgba(217,167,43,.5);color:var(--amber)}

footer{border-top:1px solid var(--hair);margin-top:4rem;padding:2.6rem 0 3.4rem;
  color:var(--grey-dim);font-size:.9rem}
footer a{color:var(--grey)}
footer .foot-brand{display:flex;align-items:center;gap:.5rem;color:var(--white);
  font-weight:640;margin-bottom:.7rem}
@media(max-width:640px){
  body{font-size:16px}
  .hero{padding:3.2rem 0 2.4rem}
  .nav-links{gap:.9rem;font-size:.84rem}
  .nav-links li:nth-child(3){display:none}
}
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

NAV = [("/specs/", "Ad specs"), ("/learn/", "Learn"),
       ("/for/", "By business"), ("/vs/", "Compare")]
DOWNLOAD = ("https://github.com/mattkerr09/adplaybook-site/releases/download/"
            "v0.1.4/AdPlaybook-0.1.4-arm64.dmg")
DL_ICON = ('<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" '
           'width="15" height="15" aria-hidden="true"><path d="M8 1.5v9m0 0L4.5 7M8 10.5 11.5 7"/>'
           '<path d="M2 11.5v2A1.5 1.5 0 0 0 3.5 15h9a1.5 1.5 0 0 0 1.5-1.5v-2"/></svg>')
TICK = ('<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2" '
        'aria-hidden="true"><path d="M2.5 8.5l3.5 3.5 7.5-8"/></svg>')


def esc(s: Any) -> str:
    return html.escape(str(s), quote=True)


def page(*, path: str, title: str, description: str, body: str,
         schema: Dict[str, Any] | None = None, modified: str = BUILT,
         wide: bool = False) -> None:
    """Write one page. `path` is the URL path, e.g. /specs/linkedin/."""
    url = BASE_URL + path
    wrapcls = "wide" if wide else "wrap"
    nav = "".join(f'<li><a href="{h}">{esc(t)}</a></li>' for h, t in NAV)
    nav += f'<li><a class="btn" href="{DOWNLOAD}">{DL_ICON}Download</a></li>'
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
<div class="{wrapcls}">{body}</div>
<footer><div class="wide">
<div class="foot-brand">{LOGO_SVG}{BRAND}</div>
<p>{esc(TAGLINE)}</p>
<p>Every figure on this site is quoted from the platform's own documentation with
the date it was read. Where something could not be verified, the page says so
rather than leaving a gap you cannot see.</p>
<p><a href="/specs/">Ad specs</a> · <a href="/learn/">Learn</a> ·
<a href="/vs/">Compare</a> · <a href="{DOWNLOAD}">Download</a> ·
<a href="/llms.txt">llms.txt</a></p>
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
            '<div class="box warn"><strong>What we could not verify</strong>'
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
    floor_html = (f'<div class="box"><strong>{esc(floor_label)}</strong><ul>{"".join(floors)}</ul>'
                  "<p>These are the numbers that decide whether a campaign delivers "
                  "at all, and none of them produces an error message when you "
                  "cross it.</p></div>" if floors else "")

    src = spec.get("source_url", "")
    check_head = ("Count these before you paste" if placements and any(
        p.get("headline_chars") or p.get("primary_text_chars") for p in placements)
        else "Check a campaign against this spec")
    title = f"{name} ad specs and character limits ({BUILT[:4]}) | {BRAND}"
    desc = (f"{name} ad character limits, image sizes and hard floors. Every "
            f"figure quoted from {name}'s own documentation with the date it was read"
            + (f", {read_on}." if read_on else "."))

    body = f"""
<article>
<p class="crumb"><a href="/specs/">Ad specs</a> / {esc(name)}</p>
<h1>{esc(name)} ad specs and character limits</h1>
<p class="lede">{esc(desc)}</p>

<div class="box ok">
<p style="margin:0"><span class="pill checked">read {esc(read_on or 'unverified')}</span>
Source: <a class="src" href="{esc(src)}" rel="nofollow noopener">{esc(src)}</a></p>
</div>

<h2>Character limits and sizes</h2>
<table><thead><tr><th>Placement</th><th>Headline</th><th>Body text</th><th>Max file</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table>
<p>Where two numbers are given, the first is what stays visible and the second
is what the field accepts. They're different questions. Copy over the cap gets
rejected at upload. Copy over the visible limit runs, and gets cut off. Most
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
<p><a class="btn" href="/#get">Get {BRAND}</a>
<a class="btn ghost" href="/specs/">All eight platforms</a></p>
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

<div class="box warn">
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

<div class="cards">{cards}</div>

<h2>Where these come from</h2>
<p>These pages are generated from the same files {BRAND} itself reads when it
builds a campaign, so the site cannot drift from the product. When a platform
changes a limit and the spec is re-checked, the page changes with it.</p>
<p><a class="btn" href="/#get">Get {BRAND}</a></p>
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
