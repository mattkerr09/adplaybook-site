"""Homepage, learn hub and comparison pages.

Split from render.py because the spec pages are generated from data and these
are written. Mixing generated and hand-written pages in one file makes it easy
to lose track of which claims came from a source file and which came from a
person — and on this site that distinction is the whole product.

The /vs/ pages follow one rule taken from the sibling project's review of its
own comparison pages: **do not state a competitor's pricing, feature list or
policy as fact.** That review found 891 extracted claims about third parties,
none independently verified, with six flagged as legal or security allegations.
The fix is not more careful wording, it is describing what this product does
and does not do, and telling the reader to check the other vendor's own page
for theirs.
"""

from __future__ import annotations

import html
from typing import Any, Callable, Dict, List

BRAND = "AdPlaybook"
REPO = "https://github.com/mattkerr09/adplaybook-site"
DMG = f"{REPO}/releases/download/v0.1.5/AdPlaybook-0.1.5-arm64.dmg"
RELEASES = f"{REPO}/releases"


def esc(s: Any) -> str:
    return html.escape(str(s), quote=True)


def build_rest(page: Callable, specs: List[Dict[str, Any]], pages: List) -> None:
    _home(page, specs)
    _learn_hub(page)
    for slug, title, desc, body in _ARTICLES:
        page(path=f"/learn/{slug}/", title=f"{title} | {BRAND}", description=desc,
             body=f'<article><p class="crumb"><a href="/learn/">Learn</a></p>'
                  f"<h1>{esc(title)}</h1><p class=\"lede\">{esc(desc)}</p>{body}</article>",
             schema={"@context": "https://schema.org", "@type": "TechArticle",
                     "headline": title, "description": desc,
                     "publisher": {"@type": "Organization", "name": BRAND}})
    _vs(page)

    from foraudience import build as build_for  # noqa: E402
    build_for(page)


def _home(page: Callable, specs: List[Dict[str, Any]]) -> None:
    names = ", ".join(s["name"] for s in specs[:-1]) + f" and {specs[-1]['name']}"
    tick = ('<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2">'
            '<path d="M2.5 8.5l3.5 3.5 7.5-8"/></svg>')
    dl = ('<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" '
          'width="15" height="15"><path d="M8 1.5v9m0 0L4.5 7M8 10.5 11.5 7"/>'
          '<path d="M2 11.5v2A1.5 1.5 0 0 0 3.5 15h9a1.5 1.5 0 0 0 1.5-1.5v-2"/></svg>')

    spec_cards = "".join(
        f'<a class="card" href="/specs/{sp["key"]}/"><strong>{esc(sp["name"])}</strong>'
        f'<span>{len(sp.get("placements", []))} placement(s), quoted and dated</span></a>'
        for sp in specs)

    body = f"""
<div class="hero">
<span class="eyebrow">{tick} Runs on your Mac. No account, no server.</span>
<h1>It writes the ad.<br><span class="grad">Then it tries to prove you wrong.</span></h1>
<p class="lede">{BRAND} turns a product page into a complete, buildable ad campaign —
strategy, audiences, exclusions, copy, test matrix, measurement plan — then attacks
its own work before it shows you anything.</p>
<div class="hero-actions">
<a class="btn" href="{{DMG}}">{dl} Download for Mac</a>
<a class="btn ghost" href="/specs/">See the ad specs</a>
</div>
<p class="hero-sub">v0.1.5 · 22 MB · Apple Silicon · notarised by Apple</p>
<div class="trust">
<span>{tick} Every claim traced to a source</span>
<span>{tick} Checked against 8 platforms' real limits</span>
<span>{tick} Nothing leaves your machine</span>
</div>
</div>

<section>
<p class="kicker">The part nobody else does</p>
<h2>It refuses to write things it cannot back up</h2>
<p>An ad that says "60-minute callouts" has to point at the page that says it.
{BRAND} harvests the exact words from your own site and blocks any figure that
is not there. Recombine two true statements into a third one nobody actually
made, and it flags that for your sign-off instead of quietly shipping it.</p>
<p>You get an <strong>evidence receipt</strong>: every claim beside the URL and
verbatim quote behind it — plus the ones needing sign-off, the ones that were
blocked, and the pages it could not read. It is built for whoever signs the ad
off and carries the liability for it.</p>
</section>

<section>
<p class="kicker">A real run, not a mockup</p>
<h2>Here is it refusing its own work</h2>
<p>This is verbatim output from pointing {BRAND} at HoneyBook's website. It
wrote three ad variants, then a second model was asked to find the reason the
campaign fails. Nothing here is illustrative.</p>

<div class="box">
<p class="src" style="margin-bottom:.6rem">VARIANT B — what it wrote</p>
<p style="margin-bottom:.2rem"><strong>All-in-one client management.</strong></p>
<p class="muted" style="margin-bottom:0">Save up to 20 hours every week. Manage
clients, projects, and payments in one place.</p>
</div>

<div class="box">
<p class="src" style="margin-bottom:.6rem">VARIANT C — blocked before anyone saw it</p>
<p style="margin-bottom:.2rem"><strong>All-in-one client management.</strong></p>
<p class="muted" style="margin-bottom:.5rem">Manage every client, project, and
payment all in one place. Starting at $29/month.</p>
<p style="margin-bottom:0"><span class="pill unchecked">blocked by the claim
gate</span> The price appears nowhere it could verify.</p>
</div>

<div class="box warn">
<p class="src" style="margin-bottom:.6rem">THE REVIEW PASS — verdict</p>
<p><strong>REJECT — 2 blockers, 1 serious.</strong></p>
<p>On Variant B: <em>"Meta will reject the ad for unqualified performance
claims… Rewrite the benefit to use unqualified language such as 'Save time
every week'."</em></p>
<p>And a strategy error nobody asked it about: optimising for Purchase on a
7-day window for a $29/month product means 50 conversions is unreachable, so
<em>"the algorithm will never exit the learning phase and the test will yield no
real results to judge the variants."</em></p>
<p style="margin-bottom:0">It also said what was good: <em>"the exclusion
strategy correctly identifies the need to exclude existing customers."</em></p>
</div>

<p>Two separate mechanisms caught the same fabricated claim without being told
to agree — the claim gate blocked the price, and the review pass flagged it
independently. That is the whole design working, on a site we do not control.</p>
<p>Every other tool in this category would have handed you all three variants.</p>
</section>

<section>
<p class="kicker">Before you spend anything</p>
<h2>It knows what will quietly fail</h2>
<p>The expensive failures in paid media do not produce an error. These are
checked by arithmetic against each platform's published limits, on every
campaign, for free:</p>
<div class="cards">
<div class="card"><span class="num">600</span><strong>Not 300</strong>
<span>LinkedIn's minimum is per ad set. Split an audience two ways and you need
600 — below that both ad sets go live and neither delivers.</span></div>
<div class="card"><span class="num">12s</span><strong>Or no funnel</strong>
<span>A YouTube video under 12 seconds builds no remarketing list, and under 10
records no views. Bumpers-then-retarget cannot work.</span></div>
<div class="card"><span class="num">1,000</span><strong>Matched users</strong>
<span>A TikTok custom audience below this cannot be used at all. Most small
customer lists do not survive matching.</span></div>
<div class="card"><span class="num">257</span><strong>Not 280</strong>
<span>X charges 23 characters for every link. Every ad has one, so copy written
to 280 does not fit.</span></div>
</div>
<p>It separates <em>the platform will refuse this</em> from <em>this will be cut
off</em>, because those need different reactions — and it tells you what it could
not check, so an empty warning list never reads as a clean bill of health.</p>
</section>

<section>
<p class="kicker">Strategy, not just words</p>
<h2>Ten approaches, each with its failure mode stated first</h2>
<p>Direct response burns your warmest audience first. Community-native gets read
by people who will argue in the replies. Retargeting recovery pays you for sales
you were going to make anyway unless you hold out a control group.</p>
<p>You are told all of that <em>before</em> you choose, because the expensive
mistakes in advertising are strategic, not typographical. {BRAND} reads your
site, works out what you sell and to whom, and recommends the approach that fits
your price, your sales cycle and your competition — then explains what it costs
you.</p>
</section>

<section>
<p class="kicker">{len(specs)} platforms</p>
<h2>Held as dated facts, not folklore</h2>
<p>{esc(names)}. Every character limit, aspect ratio and hard floor quoted from
the platform's own documentation, with the date it was read — and an explicit
list of what could not be verified.</p>
<div class="cards">{spec_cards}</div>
</section>

<section id="get">
<div class="cta-block">
<h2 style="margin-top:0">Get it</h2>
<p>Mac, Apple Silicon. Signed, notarised and stapled — it opens without a
Gatekeeper warning because Apple's notary service cleared it, not because you
right-clicked past one.</p>
<p><a class="btn" href="{{DMG}}">{dl} Download for Mac · 22 MB</a></p>
<p class="src">v0.1.5 · <a href="{{RELEASES}}">All releases</a> · needs Outlier
running locally, or an OpenAI or Anthropic key</p>
</div>
</section>

<section>
<h2>What it deliberately does not do</h2>
<p>It does not make the image or the video. What it produces is a brief specific
enough to hand to a designer or a creative generator — if the asset is what you
need, buy one of those and feed it this.</p>
<p>It does not predict performance. A conversion score on an ad that has never
run is a guess in the typography of a metric, and this tool does not publish
numbers it did not measure. In a demo that looks like a missing feature. It is
the reason to believe everything else it tells you.</p>
</section>
""".replace("{DMG}", DMG).replace("{RELEASES}", RELEASES)
    page(path="/", title=f"{BRAND} — the ad maker that proves its own claims",
         description=("Turns a product page into a complete ad campaign — strategy, "
                      "audiences, exclusions, copy and measurement — then traces every "
                      "claim to your site and checks it against each platform's real "
                      "limits before you spend anything."),
         body=body, wide=True,
         schema={"@context": "https://schema.org", "@type": "SoftwareApplication",
                 "name": BRAND, "applicationCategory": "BusinessApplication",
                 "operatingSystem": "macOS",
                 "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
                 "description": "Ad campaign generator with claim substantiation "
                                "and platform feasibility checking."})


def _learn_hub(page: Callable) -> None:
    cards = "".join(
        f'<a class="card" href="/learn/{s}/"><strong>{esc(t)}</strong>'
        f"<span>{esc(d[:95])}…</span></a>" for s, t, d, _ in _ARTICLES)
    page(path="/learn/", title=f"Learn — why ad campaigns fail quietly | {BRAND}",
         description=("Plain explanations of the ad-platform rules that break campaigns "
                      "without producing an error: audience floors, truncation, special "
                      "ad categories and attribution windows."),
         body=f'<article><p class="crumb">Learn</p>'
              "<h1>Why campaigns fail quietly</h1>"
              '<p class="lede">The expensive failures in paid media do not produce an '
              "error message. These are the ones worth knowing before you spend.</p>"
              f'<div class="cards">{cards}</div></article>')


def _vs(page: Callable) -> None:
    body = f"""
<article>
<p class="crumb">Compare</p>
<h1>{BRAND} and the creative generators</h1>
<p class="lede">These are not competing products, and pretending otherwise would
waste your time.</p>

<h2>What the creative generators do</h2>
<p>Tools like AdCreative, Creatify and Pencil produce the <strong>asset</strong>
— images and video, at volume, fast. If what you need is fifty variations of a
static ad by this afternoon, that is what they are built for and this is not.
You get a file you can upload. {BRAND}'s first output is a document.</p>
<p>We are not going to characterise their pricing or feature lists here. Those
change, we have not verified them, and a comparison page that states a
competitor's terms as fact is how you end up publishing something untrue about
someone else. Read their own pages.</p>

<h2>What {BRAND} does that they do not</h2>
<p>A different job entirely:</p>
<ul>
<li><strong>Picks the strategy.</strong> Ten approaches with their trade-offs
and failure modes, matched to your price, sales cycle and competition.</li>
<li><strong>Traces every claim.</strong> Each factual statement resolves to a
verbatim quote at a URL on your own site. Unsupported figures are blocked.</li>
<li><strong>Produces an evidence receipt</strong> a compliance reviewer can
sign — including what was blocked and what could not be read.</li>
<li><strong>Checks it will actually run</strong> against each platform's
published limits and hard floors.</li>
<li><strong>Runs a compliance pre-flight</strong> over housing, employment,
credit, health, alcohol, children, political, subscription and pricing claims,
with the statutes cited.</li>
<li><strong>Checks the landing page</strong> delivers what the ad promised —
the most expensive invisible failure in paid media.</li>
<li><strong>Runs locally.</strong> No account, no server, nothing about your
product leaves the machine.</li>
</ul>

<h2>The honest recommendation</h2>
<p>If you need the picture, buy a creative generator. If you need to know the
campaign is true, legal, and able to deliver — and to be able to prove it to
someone who is liable for it — that is this. They compose well: the brief
{BRAND} writes is a good thing to feed into one of them.</p>
<p><a class="btn" href="/#get">Get {BRAND}</a>
<a class="btn ghost" href="/specs/">See the ad specs</a></p>
</article>
"""
    page(path="/vs/", title=f"{BRAND} vs AI creative generators — a straight answer | {BRAND}",
         description=("AdPlaybook does not make images or video. Here is what it does "
                      "instead, and when a creative generator is the right purchase."),
         body=body)


# ---------------------------------------------------------------------------
# Articles. Each one answers a question somebody actually types after a
# campaign misbehaves, and each is built on a fact checked against a platform's
# own documentation rather than on a rewrite of another blog post.
# ---------------------------------------------------------------------------

from articles import ARTICLES as _ARTICLES  # noqa: E402
