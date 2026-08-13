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
DMG = f"{REPO}/releases/download/v0.1.23/AdPlaybook-0.1.23-arm64.dmg"
RELEASES = f"{REPO}/releases"


def dmg_mb(url: str = DMG) -> str:
    """The download size, measured from the DMG rather than typed.

    Follows the rule _record() already sets a few lines down — commit the script
    that derives a published figure or it goes stale silently — because the size
    had gone stale exactly that way.

    The hero and the download button both said "22 MB". The file is 22,923,679
    bytes: 22.9 in the decimal units macOS Finder reports, 21.9 in binary. Neither
    reading rounds to 22, so it was a truncation understating the download by
    about 4%, and it would only widen — the source is already twenty versions
    ahead of what this URL points at.

    Decimal with one place, which is what docketseo.app publishes (22.6 MB for
    22,562,184 bytes) and what crispvideo.app was corrected to on the same day.
    crispvideo.app had the mirror-image error: it published 74 MB, the BINARY
    figure, for a 78 MB download.

    HEAD, not GET — a build should not pull the DMG. A missing Content-Length
    raises instead of falling back to a constant: a size nobody could verify is
    not a size worth publishing.
    """
    import urllib.request

    req = urllib.request.Request(
        url, method="HEAD", headers={"User-Agent": "adplaybook-build/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        length = r.headers.get("Content-Length")
    if not length:
        raise RuntimeError(f"no Content-Length for {url} — cannot publish a size")
    return f"{int(length) / 1_000_000:.1f}"


def esc(s: Any) -> str:
    return html.escape(str(s), quote=True)



def _record() -> str:
    """The app's own measured record, read from the batch corpus at build time.

    Not hardcoded, because the rule this whole product argues for applies to
    its own marketing: commit the script that derives any published figure or
    it goes stale silently. These come from ad maker app/batch/runs/, the same
    guides scripts/sweep_report.py reads.

    Three of the four are failure rates. That is the point. Every tool in this
    category publishes the number that flatters it — this one publishes how
    often it refuses its own work, because a generator that never refuses is
    not checking anything, and a reader who knows the refusal rate can tell the
    difference. No competitor will copy this, and not because it is clever.
    """
    import glob
    from pathlib import Path as _P

    runs = sorted(glob.glob(str(_P.home() / "ad maker app" / "batch" / "runs" / "*.md")))
    all_texts = [_P(f).read_text(errors="replace") for f in runs]

    # Only guides carrying the CURRENT pipeline.
    #
    # The first draft counted all 75 and reported "38/75 checked against
    # platform limits". That is not a property of the product — it is that 37
    # guides predate 0.1.19, when the CLI did not run the feasibility check at
    # all. Published as-is it reads as "this app checks half the time", which
    # is false and is the kind of number this site exists to argue against.
    #
    # One denominator, and it is the set where every stat is measurable.
    texts = [t for t in all_texts if "Will it run?" in t]
    n = len(texts)
    if n < 10:
        return ""      # no corpus on this machine; say nothing rather than guess

    unread = sum(1 for t in texts if "could not be read" in t)
    refused = sum(1 for t in texts if "Rejected by the review" in t)
    slop = sum(1 for t in texts if "read as generated copy" in t)
    traced = sum(1 for t in texts if "Every claim in this campaign" in t)

    rows = [
        (f"{refused}<span>/{n}</span>", "campaigns its own review refused",
         "It argues with itself before it argues with you."),
        (f"{unread}<span>/{n}</span>", "sites it could not read — and said so",
         "Bot protection is common. Inventing a business is not an option."),
        (f"{slop}<span>/{n}</span>", "flagged as reading machine-written",
         "Counted, not guessed. A model cannot judge its own register."),
        (f"{traced}<span>/{n}</span>", "shipped with every claim traced",
         "Each line of copy against the page it came from, or marked unproven."),
    ]
    cells = "".join(
        f'<div class="rec"><p class="rec-n">{a}</p>'
        f'<p class="rec-l">{b}</p><p class="rec-w">{c}</p></div>'
        for a, b, c in rows)
    return (f'<section class="record"><p class="kicker">What it has actually done</p>'
            f'<h2>Three of these four are failure rates</h2>'
            f'<p class="rec-intro">Measured across {n} real businesses — every one a live '
            f'crawl through a real model, not a demo. Most tools publish the number that '
            f'flatters them. These are the ones that do not.</p>'
            f'<div class="recs">{cells}</div>'
            f'<p class="rec-src">Derived at build time from the run corpus. '
            f'<code>scripts/sweep_report.py</code> reproduces every figure.</p></section>')


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

    # Privacy, terms and contact. Through `page()` like everything else — a
    # hand-written /privacy/index.html survives the rebuild but drops out of
    # sitemap.xml every time, which is the failure that looks like success.
    from legal import build as build_legal  # noqa: E402
    build_legal(page)


def _home(page: Callable, specs: List[Dict[str, Any]]) -> None:
    names = ", ".join(s["name"] for s in specs[:-1]) + f" and {specs[-1]['name']}"
    tick = ('<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2">'
            '<path d="M2.5 8.5l3.5 3.5 7.5-8"/></svg>')
    dl = ('<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" '
          'width="15" height="15"><path d="M8 1.5v9m0 0L4.5 7M8 10.5 11.5 7"/>'
          '<path d="M2 11.5v2A1.5 1.5 0 0 0 3.5 15h9a1.5 1.5 0 0 0 1.5-1.5v-2"/></svg>')

    # Measured once per build and used in both places that print it — the hero
    # sub-line and the download button. They were two independent literals
    # saying "22 MB", which is how they came to say a number the file has not
    # been for twenty versions.
    dmg_size = dmg_mb()

    spec_cards = "".join(
        f'<a class="card" href="/specs/{sp["key"]}/"><strong>{esc(sp["name"])}</strong>'
        f'<span>{len(sp.get("placements", []))} placement(s), quoted and dated</span></a>'
        for sp in specs)

    # The third trust badge used to read "Nothing leaves your machine". It was
    # false on the page whose whole argument is that every figure it prints is
    # true. The crawl, the key and everything stored are genuinely local, but
    # the destination depends on which provider the machine can reach, so no
    # single-destination badge can be true. CORRECTION 2026-08-12: this comment
    # used to say v0.1.5 sent everything to Anthropic. It sent NOTHING —
    # dac347a:llm.py:249-258 has no `tier` parameter while every call site passes
    # `tier=`, so CPython raised TypeError binding the arguments, before any HTTP
    # request. Repeating that claim anywhere else would spread a false statement
    # about a user's data. The badge now claims only the part that holds;
    # /privacy/ carries the destination list.
    body = f"""
<div class="hero">
<h1>It writes the ad.<br><span class="grad">Then it tries to prove you wrong.</span></h1>
<p class="lede">{BRAND} turns a product page into a complete, buildable ad campaign —
strategy, audiences, exclusions, copy, test matrix, measurement plan — then attacks
its own work before it shows you anything.</p>
<div class="hero-actions">
<a class="btn" href="{{DMG}}">{dl} Download for Mac</a>
<a class="btn ghost" href="/specs/">See the ad specs</a>
</div>
<p class="hero-sub">v0.1.23 · {dmg_size} MB · Apple Silicon · notarised by Apple</p>
</div>

<section class="showcase">
<div class="win">
  <div class="win-bar">
    <span class="win-dot" style="background:#ff5f57"></span>
    <span class="win-dot" style="background:#febc2e"></span>
    <span class="win-dot" style="background:#28c840"></span>
    <span class="win-title">AdPlaybook — HoneyBook, Meta, Instagram Feed</span>
  </div>
  <div class="win-body">
    <div class="vd bad"><span class="vd-ic">&times;</span><span>
      <strong>It won't run as written</strong>2 things will stop this running</span></div>
    <div class="vd bad"><span class="vd-ic">&times;</span><span>
      <strong>Some claims could not be traced</strong>
      1 of 3 variants blocked — a price we could not trace.
      <span class="vd-quote">C — Price Axis: "Starting at $29/month" appears
      nowhere on your site. Remove it, or add the price to a page we can read.</span>
    </span></div>
    <div class="vd bad"><span class="vd-ic">&times;</span><span>
      <strong>We checked it again — do not build this</strong>
      REJECT — 2 blockers, 1 serious.</span></div>
    <div class="vd warn"><span class="vd-ic">!</span><span>
      <strong>The landing page was not checked</strong>
      No destination was given, so nothing looked at where the click lands.
      That is not the same as it being fine.</span></div>
  </div>
</div>

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
<p><a class="btn" href="{{DMG}}">{dl} Download for Mac · {dmg_size} MB</a></p>
<p class="src">v0.1.23 · <a href="{{RELEASES}}">All releases</a> · needs Outlier
running locally, or an OpenAI or Anthropic key</p>
</div>
<p class="win-cap"><span>A real run, not a mockup.</span> Verbatim output from
pointing {BRAND} at HoneyBook's website. It wrote three ad variants, then a
second model was asked to find the reason the campaign fails. Nothing here is
illustrative.</p>
</section>

{_record()}

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
<li><strong>Runs on your Mac.</strong> No account and no server of ours. With
Outlier answering locally, nothing about your product leaves the machine; without
it, the writing goes to Claude on your own key — see
<a href="/privacy/">what this sends and where</a>.</li>
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
