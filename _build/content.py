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
import re
from typing import Any, Callable, Dict, List

BRAND = "AdPlaybook"
REPO = "https://github.com/mattkerr09/adplaybook-site"
RELEASES = f"{REPO}/releases"


def _latest_dmg() -> str:
    """The download URL, asked of GitHub rather than carried in this file.

    This line used to read:

        DMG = f"{REPO}/releases/download/v0.1.23/AdPlaybook-0.1.23-arm64.dmg"

    and it was correct. v0.1.23 genuinely was the newest release a stranger could
    download, so every check passed and the site was not stale. What made it a
    problem is what sat behind it: the app repo shipped twelve builds on
    2026-08-13 and published none of them, because nothing in it called
    `gh release`. The hardcoded URL was true only because the pipeline it pointed
    at had stopped moving. Give that pipeline a publish step — which
    scripts/publish_release.sh in the app repo now is — and this line becomes a
    falsehood on the first ship, silently, with the site still passing its own
    checks because a hardcoded URL cannot disagree with itself.

    So it is derived now, from the same place a visitor would look. Same rule as
    dmg_mb() below and _record() further down: commit the code that derives a
    published figure, or the figure goes stale without anything noticing.

    The fallback matters as much as the lookup. If the API is unreachable — no
    network during a build, rate limiting, an outage — this returns the releases
    PAGE rather than guessing at a version-shaped URL. A visitor who lands on the
    releases list can still get the product; a visitor who follows an invented
    URL gets a 404 and concludes the download is broken. Degrade toward a place
    that is always true.
    """
    import json
    import urllib.error
    import urllib.request

    api = "https://api.github.com/repos/mattkerr09/adplaybook-site/releases/latest"
    req = urllib.request.Request(
        api, headers={"User-Agent": "adplaybook-site-build",
                      "Accept": "application/vnd.github+json"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            data = json.load(r)
    except (urllib.error.URLError, urllib.error.HTTPError, OSError, ValueError):
        return RELEASES

    for asset in data.get("assets", []):
        url = asset.get("browser_download_url", "")
        if url.endswith("-arm64.dmg"):
            return url
    return RELEASES


DMG = _latest_dmg()


def _latest_tag() -> str:
    """The version shown beside the download button.

    This read a literal "v0.1.23" until 2026-08-13, in the same file and eight
    lines from the DMG URL I had derived an hour earlier. Fixing one hardcoded
    version and leaving its sibling is the shape of nearly everything found
    today: the obvious instance gets corrected, the copy nobody thought about
    keeps the old value, and the two never disagree because nothing compares
    them.

    It is taken from the DMG URL rather than fetched again, so the version and
    the file a visitor downloads cannot drift apart — one lookup, one answer.
    """
    m = re.search(r"/releases/download/(v[^/]+)/", DMG)
    return m.group(1) if m else ""


VERSION_TAG = _latest_tag()

#: Price and checkout. Set 2026-08-14 from competitor research rather than by
#: asking Matthew a fourth time.
#:
#: Every rival in this category is a subscription with a meter: AdCreative.ai
#: from $39/mo on 10 credits, Creatopy from $39/mo, Pencil from $14/mo on 50
#: generations. A year of the cheapest is $168 and the credits run out. This is
#: $149 once, unmetered, forever — cheaper than one year of anything it competes
#: with, and it can be, because the app runs on the user's own model or API key
#: so there is no inference cost to cover.
#:
#: Free on ONE website with nothing held back. Not a trial, not a watermark, not
#: a credit counter. A tool whose whole argument is that it refuses claims it
#: cannot substantiate cannot ask to be trusted from behind a paywall — the buyer
#: watches it work end to end on their own site, then pays to point it anywhere.
# CORRECTED 2026-08-14, one hour after shipping it. The first copy said "free
# forever on ONE website" and "$149 removes the one-site limit". THE APP HAS NO
# SUCH LIMIT — there is no entitlement code in the repo at all, so the site was
# selling the removal of a restriction that does not exist. That is the exact
# class of falsehood this project spent two days deleting from other pages, and I
# introduced it while fixing something else.
#
# The copy now describes what is actually true: the app is free to download and
# use, and $149 buys a LICENCE for unlimited commercial use. A licence term is
# real whether or not code enforces it. Once the domain gate ships, the stronger
# framing can come back — and not before.
PRICE_USD = 149
PRICE_STR = f"${PRICE_USD}"

def _bnpl_section() -> str:
    """The pay-in-4 block, or nothing at all.

    TWO CONDITIONS, NOT ONE. `BNPL_LIVE` is a human's intent; `checkout_provider()`
    is what the Buy button actually does. Publishing on intent alone is how a page
    ends up promising instalments at a card-only checkout — which on THIS product,
    whose pitch is that it refuses claims it cannot trace, would be the worst
    possible sentence to get wrong.

    Returns "" rather than raising, because a missing section is a quiet nothing
    and check.py fails the build if the flag is set and the copy is absent. The
    gate catches it; the page never lies while we wait.
    """
    import bnpl
    if bnpl.BNPL_LIVE and bnpl.checkout_provider() == "dodo":
        return bnpl.SECTION
    return ""

CHECKOUT = "https://checkout.dodopayments.com/buy/pdt_0NlgduBtaHbj0V2WvTCqG"


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
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            length = r.headers.get("Content-Length")
    except Exception:  # noqa: BLE001
        # The same reasoning as the missing-Content-Length branch below, and it
        # has to be here too: on a real outage urlopen RAISES before any header
        # is read, so handling only the missing-header case still let a network
        # blip kill the build. Found by simulating the outage rather than
        # reasoning about it — the first version of this fix looked complete
        # and died one line earlier.
        return ""
    if not length:
        # No size rather than a wrong size — and no dead build either.
        #
        # This raised, and the raise was half right. _latest_dmg() degrades to
        # the releases PAGE when GitHub's API is unreachable, deliberately:
        # "degrade toward a place that is always true". That page is HTML with
        # no Content-Length, so the graceful fallback fed straight into a fatal
        # one and the whole site became unbuildable during an API blip.
        #
        # Hit for real on 2026-08-18: `no Content-Length for
        # .../releases — cannot publish a size`, with the API answering 200
        # and 52/60 rate limit left a minute later. It was a blip, and a blip
        # must not be able to stop a build.
        #
        # It matters because publish_release.sh treats a failed site build as
        # fatal AFTER the release is already published — "the release exists
        # but nothing links it". So a two-second GitHub hiccup during a ship
        # breaks the ship at its worst moment.
        #
        # The guarantee the raise protected is kept: no size is ever guessed.
        # The caller omits the figure instead.
        return ""
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
    return (f'<section class="record"><p class="kicker reveal">What it has actually done</p>'
            f'<h2>Three of these four are failure rates</h2>'
            f'<p class="rec-intro">Measured across {n} real businesses — every one a live '
            f'crawl through a real model, not a demo. Most tools publish the number that '
            f'flatters them. These are the ones that do not.</p>'
            f'<div class="recs">{cells}</div>'
            f'<p class="rec-src">Derived at build time from the run corpus. '
            f'<code>scripts/sweep_report.py</code> reproduces every figure.</p></section>')


def _selfcheck() -> str:
    """The product's own verdict on an ad written for the product.

    Read from _build/selfcheck.json, which `_build/selfcheck.py` regenerates by
    crawling this site and running `adkit.gate` and `adkit.feasibility` — the
    same modules the shipped app runs. Same doctrine as `_record()`: commit the
    script that derives a published figure, or it goes stale silently.

    The section says plainly that the three variants were written by hand and
    the verdicts were not. That distinction is the entire honesty of the page,
    and the HoneyBook showcase above it earns its "verbatim" caption precisely
    because docs/EVIDENCE.md records the run that produced it. This one is
    weaker in one way — no model wrote the copy — and stronger in another: the
    reader can go and check the site it was run against, because it is this one.

    Returns "" when the JSON is absent, rather than inventing a specimen.
    """
    import json
    from pathlib import Path as _P

    f = _P(__file__).resolve().parent / "selfcheck.json"
    if not f.exists():
        return ""
    try:
        d = json.loads(f.read_text())
    except (ValueError, OSError):
        return ""

    gate_d, feas = d.get("gate", {}), d.get("feasibility", {})
    blocked = set(gate_d.get("blocked", []))
    claims = gate_d.get("claims", [])

    # The one claim that resolved to a real span, with the page it was found
    # on. A gate that only ever says no is a filter, not a check — showing the
    # substantiated case is what makes the blocked ones mean something.
    proved = next((c for c in claims
                   if c.get("verdict") == "substantiated" and c.get("source_url")), None)
    failed = [c for c in claims if c.get("verdict") == "unsubstantiated"]

    rows = []
    if proved:
        rows.append(
            f'<div class="vd ok"><span class="vd-ic">&check;</span><span>'
            f'<strong>Substantiated &mdash; and here is where</strong>'
            f'{esc(proved["text"])}'
            f'<span class="vd-quote">Found on '
            f'<a href="{esc(proved["source_url"])}">{esc(proved["source_url"])}</a>. '
            f'A claim the gate can point at is a claim you can sign off.</span>'
            f'</span></div>')
    if failed:
        first = failed[0]
        rows.append(
            f'<div class="vd bad reveal"><span class="vd-ic">&times;</span><span>'
            f'<strong>{len(blocked)} of {len(d.get("variants", []))} variants blocked</strong>'
            f'{esc(gate_d.get("summary", ""))}'
            f'<span class="vd-quote">{esc(first["text"])} &mdash; '
            f'{esc(first.get("note", ""))}</span></span></div>')

    undeclared = [c for c in failed if c.get("undeclared")]
    if undeclared:
        rows.append(
            f'<div class="vd bad reveal"><span class="vd-ic">&times;</span><span>'
            f'<strong>{len(undeclared)} it caught that the campaign never declared</strong>'
            f'The copy was scanned for claim-shaped language as well as checked '
            f'against the list it declared, because a generator that under-reports '
            f'its own claims would otherwise sail through.</span></div>')

    for i in feas.get("issues", [])[:2]:
        rows.append(
            f'<div class="vd warn reveal"><span class="vd-ic">!</span><span>'
            f'<strong>{esc(i["where"])}</strong>{esc(i["what"])}'
            + (f'<span class="vd-quote">{esc(i["quote"])}<br>'
               f'<strong style="display:inline">Fix:</strong> {esc(i["fix"])}</span>'
               if i.get("quote") else "")
            + '</span></div>')

    not_checked = "".join(f"<li>{esc(x)}</li>" for x in feas.get("not_checked", []))
    variants = "".join(
        f'<div class="box{" warn" if v["label"] in blocked else ""}">'
        f'<p class="src" style="margin-bottom:.6rem">{esc(v["label"].upper())}'
        + ('<span class="pill unchecked" style="margin-left:.5rem">blocked</span>'
           if v["label"] in blocked else "")
        + f'</p><p style="margin-bottom:.2rem"><strong>{esc(v["headline"])}</strong></p>'
        f'<p class="muted" style="margin-bottom:0">{esc(v["primary_text"])}</p></div>'
        for v in d.get("variants", []))

    return f"""
<section class="showcase">
<p class="kicker reveal">Run against ourselves</p>
<h2>We pointed it at this website</h2>
<p>Everything above describes what the gate does. This is it doing it &mdash; to
an ad for {BRAND}, checked against {BRAND}&rsquo;s own site, which you are
reading and can go and check yourself.</p>

<div class="win">
  <div class="win-bar">
    <span class="win-dot" style="background:#ff5f57"></span>
    <span class="win-dot" style="background:#febc2e"></span>
    <span class="win-dot" style="background:#28c840"></span>
    <span class="win-title">{BRAND} &mdash; adplaybook.app, {esc(d.get("platform", ""))}</span>
  </div>
  <div class="win-body">{"".join(rows)}</div>
</div>

{variants}

<div class="box reveal">
<p class="src" style="margin-bottom:.6rem">WHAT IT COULD NOT CHECK</p>
<ul style="margin:0;padding-left:1.1rem;color:var(--grey);font-size:.9rem;line-height:1.6">{not_checked}</ul>
<p class="src" style="margin:.7rem 0 0">An empty warning list has to mean
&ldquo;checked and clean&rdquo;, never &ldquo;did not look&rdquo;. This is the
part every other tool leaves out, and it is the reason to believe the rest.</p>
</div>

<p class="win-cap"><span>Who wrote what.</span> The three variants were written
by hand, here, so the specimen does not change between builds. Every verdict
under them was not: they come from <code>adkit.gate</code> and
<code>adkit.feasibility</code>, the same modules the app runs, against a live
crawl of this site that read {d.get("crawl", {}).get("spans", 0)} spans.
Produced on {esc(d.get("generated_on", ""))} against {BRAND}
{esc(d.get("app_version", ""))}. <code>_build/selfcheck.py</code> reproduces it.</p>

<p class="win-cap"><span>One page was held out, and here is why.</span> The crawl
behind this skips <em>this</em> page. It has to: the section you are reading
quotes variant C word for word, so the next crawl read those sentences back off
our own site and cleared all three variants &mdash; the invented claims had
become true statements about the page that printed them. Every other page was
read, which is why &ldquo;Eight platforms&rdquo; still resolves: it lives on
<a href="/for/agencies/">/for/agencies/</a> and was there long before this
existed. A check that reads what it just wrote is checking itself.</p>
</section>
"""


def build_rest(page: Callable, specs: List[Dict[str, Any]], pages: List,
               app_repo=None) -> None:
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

    # One page per strategy, read from the app's own loadout files. The site
    # had a page for every platform and none for any strategy, which is
    # backwards — the specs are facts anyone can look up on Meta's site, and
    # the ten strategies are the thing this product actually decides.
    from strategies import build as build_strategies  # noqa: E402
    if app_repo is not None:
        build_strategies(page, app_repo)

        # The offline models. Shipped in 0.2.23 with no page at all, which was
        # the largest gap on the site: it is the only claim here most
        # competitors cannot make.
        from offline import build as build_offline  # noqa: E402
        build_offline(page, app_repo)

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
    # Empty when the asset could not be measured. Both call sites drop the
    # whole segment rather than print "· MB" or a bare number.
    size_bit = f" {dmg_size} MB ·" if dmg_size else ""
    size_suffix = f" · {dmg_size} MB" if dmg_size else ""

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
<p class="kicker reveal">AD CAMPAIGNS, WITH THE REASONING SHOWN</p>
<div class="hero-split">
<div class="hero-lead">
<h1>It writes the ad.<br><span class="grad">Then it tries to prove you wrong.</span></h1>
</div>
<div class="hero-aside">
<p class="lede">{BRAND} turns a product page into a complete, buildable ad campaign —
strategy, audiences, exclusions, copy, test matrix, measurement plan — then attacks
its own work before it shows you anything.</p>
<div class="hero-actions">
<a class="btn" href="{{DMG}}">{dl} Download for Mac</a>
<a class="btn ghost" href="/specs/">See the ad specs</a>
</div>
<p class="hero-sub">{VERSION_TAG} ·{size_bit} Apple Silicon · notarised by Apple</p>
</div>
</div>
</div>

<!-- The six stages of the run shown below it.
     Figures are that SAME run, from docs/EVIDENCE.md in the app repo, so the
     strip and the window are one campaign rather than two stitched together.
     There is no live badge and no counter, because neither would be wired to
     anything. -->
<ol class="stages">
<li><span class="stage-n">1</span><strong>Read</strong>
    <span class="stage-d">6 pages · 116 spans · quality 1.00</span></li>
<li><span class="stage-n">2</span><strong>Brief</strong>
    <span class="stage-d">what is provably true about the product</span></li>
<li><span class="stage-n">3</span><strong>Generate</strong>
    <span class="stage-d">3 variants, one axis apart</span></li>
<li><span class="stage-n">4</span><strong>Claim gate</strong>
    <span class="stage-d">1 blocked — a price it could not trace</span></li>
<li><span class="stage-n">5</span><strong>Review</strong>
    <span class="stage-d">REJECT — 2 blockers</span></li>
<li><span class="stage-n">6</span><strong>Guide</strong>
    <span class="stage-d">15,884 bytes, in build order</span></li>
</ol>

<section class="showcase">
<div class="win">
  <div class="win-bar">
    <span class="win-dot" style="background:#ff5f57"></span>
    <span class="win-dot" style="background:#febc2e"></span>
    <span class="win-dot" style="background:#28c840"></span>
    <span class="win-title">AdPlaybook — HoneyBook, Meta, Instagram Feed</span>
  </div>
  <div class="win-body">
    <div class="vd bad reveal"><span class="vd-ic">&times;</span><span>
      <strong>It won't run as written</strong>2 things will stop this running</span></div>
    <div class="vd bad reveal"><span class="vd-ic">&times;</span><span>
      <strong>Some claims could not be traced</strong>
      1 of 3 variants blocked — a price we could not trace.
      <span class="vd-quote">C — Price Axis: "Starting at $29/month" appears
      nowhere on your site. Remove it, or add the price to a page we can read.</span>
    </span></div>
    <div class="vd bad reveal"><span class="vd-ic">&times;</span><span>
      <strong>We checked it again — do not build this</strong>
      REJECT — 2 blockers, 1 serious.</span></div>
    <div class="vd warn reveal"><span class="vd-ic">!</span><span>
      <strong>The landing page was not checked</strong>
      No destination was given, so nothing looked at where the click lands.
      That is not the same as it being fine.</span></div>
  </div>
</div>

<div class="box reveal">
<p class="src" style="margin-bottom:.6rem">VARIANT B — what it wrote</p>
<p style="margin-bottom:.2rem"><strong>All-in-one client management.</strong></p>
<p class="muted" style="margin-bottom:0">Save up to 20 hours every week. Manage
clients, projects, and payments in one place.</p>
</div>

<div class="box reveal">
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
<p class="kicker reveal">Before you spend anything</p>
<h2>It knows what will <span class="grad">quietly fail</span></h2>
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
<p class="kicker reveal">Strategy, not just words</p>
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
<p class="kicker reveal">{len(specs)} platforms</p>
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
<p><a class="btn" href="{{DMG}}">{dl} Download free for Mac{size_suffix}</a>
<a class="btn ghost" href="{{CHECKOUT}}" style="margin-left:.6rem">Buy a licence · {{PRICE_STR}} once</a></p>
{{BNPL}}
<p class="src"><strong>30 days to change your mind.</strong> If it does not do what
you need, email within 30 days of purchase and we refund in full — no reason
required, back to the original payment method. One refund per customer, and the
full policy is in the <a href="/terms/">terms</a>.</p>
<p class="src">Free to download and use — the whole app, no credits, no watermark, no account. {{PRICE_STR}} once buys a licence for unlimited commercial use across every site you work on. No subscription and no renewal.</p>
<p class="src">{VERSION_TAG} · <a href="{{RELEASES}}">All releases</a> · needs Outlier
running locally, or an OpenAI or Anthropic key</p>
</div>
<figure class="adshot reveal">
  <img src="/img/honeybook-a-control-preview.svg" width="460" height="808"
       alt="Ad preview drawn by AdPlaybook: primary text 61 of 90 characters,
            headline 27 of 30, description 54 of 90, for a Google Ads
            responsive search ad." loading="lazy">
  <figcaption><span>Drawn by the app, from this run.</span> Variant A as it will
  run, with every field counted against Google's published limits and the page
  those limits were read from printed underneath. Downloaded from the result
  screen as <code>a-control-preview.svg</code> — this is the file, not a picture
  of it.</figcaption>
</figure>

<figure class="appshot reveal">
  <div class="appshot-chrome" aria-hidden="true">
    <span class="win-dot" style="background:#ff5f57"></span>
    <span class="win-dot" style="background:#febc2e"></span>
    <span class="win-dot" style="background:#28c840"></span>
    <span class="appshot-title">AdPlaybook — the run that produced everything above</span>
  </div>
  <img src="/img/app-03-result.png" width="1600" height="1075" loading="lazy"
       alt="AdPlaybook's result screen: every claim traced to your site, all 2
            variants cleared the claim gate, 1 blocker and 2 serious findings
            from the review pass, and the landing page not checked.">
  <figcaption><span>The app, on the run above.</span> Not a mockup and not a
  recording of a stub — AdPlaybook v0.2.48 pointed at HoneyBook, crawled and
  generated through a real model, photographed at the moment it finished. The
  verdicts in the window are the ones it produced that time, including the two
  it could not check.</figcaption>
</figure>

<p class="win-cap"><span>A real run, not a mockup.</span> Verbatim output from
pointing {BRAND} at HoneyBook's website. It wrote three ad variants, then a
second model was asked to find the reason the campaign fails. Nothing here is
illustrative.</p>
</section>

{_livegate_section()}

{_record()}

<section>
<p class="kicker reveal">The part nobody else does</p>
<h2>It refuses to write things <span class="grad">it cannot back up</span></h2>
<p>An ad that says "60-minute callouts" has to point at the page that says it.
{BRAND} harvests the exact words from your own site and blocks any figure that
is not there. Recombine two true statements into a third one nobody actually
made, and it flags that for your sign-off instead of quietly shipping it.</p>
<p>You get an <strong>evidence receipt</strong>: every claim beside the URL and
verbatim quote behind it — plus the ones needing sign-off, the ones that were
blocked, and the pages it could not read. It is built for whoever signs the ad
off and carries the liability for it.</p>
</section>

{_selfcheck()}

<section>
<h2>What it <span class="grad">deliberately does not do</span></h2>
<p>It does not make the image or the video. What it produces is a brief specific
enough to hand to a designer or a creative generator — if the asset is what you
need, buy one of those and feed it this.</p>
<p>It does not predict performance. A conversion score on an ad that has never
run is a guess in the typography of a metric, and this tool does not publish
numbers it did not measure. In a demo that looks like a missing feature. It is
the reason to believe everything else it tells you.</p>
</section>
""".replace("{DMG}", DMG).replace("{RELEASES}", RELEASES).replace("{CHECKOUT}", CHECKOUT).replace("{BNPL}", _bnpl_section()).replace("{PRICE_STR}", PRICE_STR)
    page(path="/", title=f"{BRAND} — the ad maker that proves its own claims",
         description=("Turns a product page into a complete ad campaign — strategy, "
                      "audiences, exclusions, copy and measurement — then traces every "
                      "claim to your site and checks it against each platform's real "
                      "limits before you spend anything."),
         body=body, wide=True,
         schema={"@context": "https://schema.org", "@type": "SoftwareApplication",
                 "name": BRAND, "applicationCategory": "BusinessApplication",
                 "operatingSystem": "macOS",
                 # Interpolated, never typed. This said "0" for a $149 product
                 # from 2026-08-10 until 2026-08-17: written before there was a
                 # price, and the pricing commit rewrote the CTA and licence copy
                 # in this same function while missing the schema fifty lines
                 # below. It is the ONLY machine-readable price on all 49 pages,
                 # and robots.txt explicitly welcomes GPTBot, ClaudeBot,
                 # OAI-SearchBot and PerplexityBot — so "how much does AdPlaybook
                 # cost?" was being answered "free" by every AI that asked.
                 "offers": {"@type": "Offer", "price": str(PRICE_USD),
                            "priceCurrency": "USD",
                            "description": f"One-time licence for unlimited "
                                           f"websites. Free forever on one site."},
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
<p>We used to say nothing at all about their pricing here, on the grounds that
it changes and we had not checked it. That was the right call while it was true.
It has now been checked, so here is the one comparison that actually decides
things, dated and sourced so you can hold us to it.</p>
<p><strong>As of 14 August 2026, per each vendor's own published pricing:</strong>
Jasper starts at $59/month billed annually ($69 month-to-month). Copy.ai starts
around $29/month. AdCreative.ai starts at $20/month billed yearly ($39 month-to-month) and runs to
$500/month billed yearly ($999 month-to-month) at its top tier. {BRAND} is <strong>${PRICE_USD} once</strong>.</p>
<p>What that means in practice: the cheapest of them passes our price in the eighth
month and Jasper passes it in the third, and after that they keep going. This
is the whole of our pricing argument and we would rather write it down than imply
it. Check their pages &mdash; ours is dated because theirs will change, and if
this paragraph is stale when you read it, that is our fault and not theirs.</p>
<p>We still will not characterise their FEATURES. Those move faster than pricing,
we do not use these tools daily, and a feature table written by a competitor is
worth exactly what you paid for it. Read their own pages for what they do.</p>

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

#: The live claim gate — markup and script, as module constants.
#:
#: These lived in _build/livegate.py until the served-internals ratchet in
#: check.py refused it: every tracked file here is a public URL, and a new
#: module is a new one. The ratchet exists to hold that exposure at zero
#: growth, and the first thing it caught was mine. Weakening it by adding the
#: file to its own baseline would have been the wrong way round, so the code
#: moved into a file that is already on the list instead.
#:
#: Kept out of the f-string above because the script is full of braces that
#: would each have to be doubled — the kind of edit that yields a page which
#: renders and a script that silently never runs.
LIVEGATE_SECTION = '\n<section class="livegate" id="try">\n  <p class="eyebrow reveal">Try the claim gate</p>\n  <h2>Paste an ad claim. Watch it get checked.</h2>\n  <p class="livegate-lede">This is the real gate — the same thirteen patterns\n  the app runs, exported from the engine, not a reproduction. Nothing is sent\n  anywhere; it runs in this page.</p>\n\n  <div class="lg-grid">\n    <label class="lg-field">\n      <span>Your ad copy</span>\n      <textarea id="lg-claim" rows="4" spellcheck="false">Trusted by 4,000 businesses. Get paid 10x faster. Starting at $29/month.</textarea>\n    </label>\n    <label class="lg-field">\n      <span>Text from your website</span>\n      <textarea id="lg-source" rows="4" spellcheck="false">HoneyBook helps independent businesses manage clients, projects and payments in one place. Plans from $19/month.</textarea>\n    </label>\n  </div>\n\n  <div class="lg-out" id="lg-out" aria-live="polite"></div>\n  <p class="lg-foot">A claim it cannot trace to your own page is blocked before\n  it reaches an ad account. That is the whole product; this is it running.</p>\n</section>\n'

LIVEGATE_SCRIPT = '\n<script id="lg-data" type="application/json">{"_note":"Generated by scripts/export_gate_patterns.py from backend/adkit/gate.py. Do not edit by hand \\u2014 tests/test_gate_export.py fails when this drifts from the engine.","figure_re":"[$\\u00a3\\u20ac]?\\\\d[\\\\d,.]*\\\\s*(?:k\\\\b|m\\\\b|bn\\\\b|b\\\\b|x\\\\b|%|\\\\+)?","claim_patterns":[{"pattern":"\\\\b\\\\d[\\\\d,.]*\\\\s?(?:k|m|\\\\+|million|thousand|%)?\\\\s+(?:customers?|clients?|users?|teams?|businesses|companies|reviews?|stars?|years?|countries|downloads?|installs?)\\\\b","label":"a quantity of people or time"},{"pattern":"\\\\btrusted by\\\\b|\\\\bloved by\\\\b|\\\\bused by\\\\b|\\\\bjoin \\\\d","label":"social proof"},{"pattern":"\\\\b(?:no\\\\.?\\\\s?1|#1|the (?:best|leading|top|only|fastest|largest))\\\\b","label":"a superlative"},{"pattern":"\\\\b(?:award[- ]winning|voted|rated|certified|accredited|licen[cs]ed)\\\\b","label":"a credential"},{"pattern":"\\\\b(?:guarantee[ds]?|money[- ]back|risk[- ]free|refund)\\\\b","label":"a guarantee"},{"pattern":"\\\\b(?:in|within|under)\\\\s+\\\\d+\\\\s?(?:min|minute|hour|day|week|second)","label":"a speed promise"},{"pattern":"\\\\b(?:free|save|from)\\\\s*[$\\u00a3\\u20ac]\\\\s?\\\\d|[$\\u00a3\\u20ac]\\\\s?\\\\d[\\\\d,.]*","label":"a price"},{"pattern":"\\\\b\\\\d[\\\\d,.]*\\\\s?%","label":"a percentage"},{"pattern":"\\\\b(?:save|cut|reduce|increase|grow|double|triple)\\\\s+(?:your\\\\s+)?\\\\w+\\\\s+by\\\\b","label":"a quantified outcome"},{"pattern":"\\\\b\\\\d+\\\\s?x\\\\s+(?:faster|quicker|more|less|better|cheaper|higher|bigger)","label":"a performance multiplier"},{"pattern":"\\\\b(?:twice|thrice|three times|four times|double|triple|half)\\\\s+(?:as\\\\s+)?(?:fast|quick|many|much|long|the)\\\\b","label":"a performance multiplier"},{"pattern":"\\\\b(?:faster|quicker|cheaper|better|easier|simpler|more)\\\\s+than\\\\b","label":"a comparison to something else"},{"pattern":"\\\\b(?:instantly|overnight|in seconds|same[- ]day|next[- ]day)\\\\b","label":"a speed promise"}]}</script>\n<script>\n/* The live claim gate.\n *\n * The patterns are EXPORTED from backend/adkit/gate.py and a test in the app\n * repo runs the same strings through Python\'s `re` and node\'s RegExp and fails\n * if the verdicts differ. So this is the engine\'s rule, not a reproduction of\n * it — which matters, because a page that fakes its own product\'s output is\n * the exact thing this product exists to catch.\n *\n * The figure trace is the gate\'s second half: a number in the ad must appear\n * in text the crawler actually read. Bounded so "20" is not satisfied by\n * "120", same as _figure_is_present.\n */\n(function(){\n  var el = document.getElementById(\'lg-out\');\n  if (!el) return;\n  var data = JSON.parse(document.getElementById(\'lg-data\').textContent);\n  var claimEl = document.getElementById(\'lg-claim\');\n  var srcEl = document.getElementById(\'lg-source\');\n  var FIG = new RegExp(data.figure_re, \'gi\');\n\n  function figures(text){\n    var out = [], m;\n    FIG.lastIndex = 0;\n    while ((m = FIG.exec(text)) !== null) {\n      var raw = m[0].trim().toLowerCase()\n        .replace(/^[$£€]/, \'\').replace(/[.,]+$/, \'\').replace(/,/g, \'\');\n      if (raw && /\\d/.test(raw)) out.push(raw);\n      if (m.index === FIG.lastIndex) FIG.lastIndex++;\n    }\n    return out;\n  }\n  function present(fig, source){\n    var bare = fig.replace(/[kmbx%+]+$/, \'\').replace(/\\.$/, \'\');\n    if (!bare) return false;\n    return new RegExp(\'(?<!\\\\d)\' + bare.replace(/[.*+?^${}()|[\\]\\\\]/g,\'\\\\$&\') + \'(?!\\\\d)\')\n      .test(source);\n  }\n  function esc(s){ return s.replace(/[&<>]/g, function(c){\n    return {\'&\':\'&amp;\',\'<\':\'&lt;\',\'>\':\'&gt;\'}[c]; }); }\n\n  function run(){\n    var claim = claimEl.value, source = srcEl.value;\n    var rows = [];\n    /* Widen each match to its surrounding sentence before tracing figures —\n       a faithful port of _find_undeclared in gate.py, including MAX_SPAN=160.\n       Using the bare regex match instead was a real bug caught by running\n       this: the price pattern matches only "from $1" of "from $19/month", so\n       the figure traced was "1" and a price that IS on the advertiser\'s page\n       came back BLOCKED. That is the page showing a verdict the engine does\n       not give, on the one product whose pitch is that it proves its claims. */\n    var MAX_SPAN = 160;\n    data.claim_patterns.forEach(function(p){\n      var re = new RegExp(p.pattern, \'gi\'), m;\n      while ((m = re.exec(claim)) !== null) {\n        var start = Math.max(\n          claim.lastIndexOf(\'.\', m.index - 1) + 1,\n          claim.lastIndexOf(\'!\', m.index - 1) + 1,\n          claim.lastIndexOf(\'?\', m.index - 1) + 1,\n          m.index - MAX_SPAN, 0);\n        var endsAt = [\'.\', \'!\', \'?\']\n          .map(function(ch){ return claim.indexOf(ch, m.index + m[0].length); })\n          .filter(function(i){ return i !== -1; });\n        var end = endsAt.length ? Math.min.apply(null, endsAt) : claim.length;\n        end = Math.min(end, m.index + m[0].length + MAX_SPAN);\n        var span = claim.slice(start, end).replace(/^[\\s.,!?]+|[\\s.,!?]+$/g, \'\');\n        if (span) rows.push({ text: span, why: p.label });\n        if (m.index === re.lastIndex) re.lastIndex++;\n      }\n    });\n    var seen = {}, uniq = [];\n    rows.forEach(function(r){ var k = r.text.toLowerCase();\n      if (!seen[k]) { seen[k] = 1; uniq.push(r); } });\n\n    var blocked = 0, html = \'\';\n    uniq.forEach(function(r){\n      var figs = figures(r.text);\n      var missing = figs.filter(function(f){ return !present(f, source); });\n      var ok = missing.length === 0;\n      if (!ok) blocked++;\n      html += \'<div class="lg-row \' + (ok ? \'ok\' : \'bad\') + \'">\' +\n        \'<span class="lg-ic">\' + (ok ? \'✓\' : \'×\') + \'</span><span>\' +\n        \'<strong>\' + esc(r.text) + \'</strong>\' +\n        \'<span class="lg-why">\' + esc(r.why) +\n        (ok ? (figs.length ? \' — traced to your page\'\n                           : \' — needs a source on your page\')\n            : \' — \' + esc(missing.join(\', \')) +\n              \' appears nowhere in the text you gave\') +\n        \'</span></span></div>\';\n    });\n\n    if (!uniq.length) {\n      html = \'<div class="lg-row ok"><span class="lg-ic">✓</span><span>\' +\n        \'<strong>Nothing here needs substantiating</strong>\' +\n        \'<span class="lg-why">No price, superlative, guarantee, statistic or \' +\n        \'performance promise found. That is a pass, not an endorsement.</span>\' +\n        \'</span></div>\';\n    }\n    var verdict = blocked\n      ? \'<p class="lg-verdict bad">BLOCKED — \' + blocked +\n        (blocked === 1 ? \' claim\' : \' claims\') + \' could not be traced.</p>\'\n      : \'<p class="lg-verdict ok">\' + uniq.length +\n        (uniq.length === 1 ? \' claim\' : \' claims\') + \' checked, all traced.</p>\';\n    el.innerHTML = verdict + html;\n  }\n\n  claimEl.addEventListener(\'input\', run);\n  srcEl.addEventListener(\'input\', run);\n  run();\n})();\n</script>\n'


def _livegate_section() -> str:
    return LIVEGATE_SECTION + LIVEGATE_SCRIPT

