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


def _home(page: Callable, specs: List[Dict[str, Any]]) -> None:
    names = ", ".join(s["name"] for s in specs[:-1]) + f" and {specs[-1]['name']}"
    body = f"""
<div class="hero">
<h1>It writes the ad. Then it tries to prove you wrong.</h1>
<p class="lede">{BRAND} turns a product page into a complete, buildable ad
campaign — the strategy, the audiences, the exclusions, the copy, the test
matrix and the measurement plan — and then attacks its own work before it shows
you anything.</p>
<p><a class="cta" href="/#get">Get it for Mac</a>
<a class="cta ghost" href="/specs/">See the ad specs</a></p>
</div>

<h2>It picks the strategy, not just the words</h2>
<p>Ten strategies, each with its own copy constraints, its own definition of
success, and — stated before you choose it — <em>how it usually fails</em>.
Direct response burns your warmest audience first. Community-native gets read by
people who will argue in the replies. You are told that up front, because the
expensive mistakes in advertising are strategic, not typographical.</p>
<p>It reads your site, works out what you actually sell and to whom, then
recommends the approach that fits your price, your sales cycle and your
competition — and explains what that approach costs you.</p>

<h2>Every claim traces to a line on your site</h2>
<p>An ad that says "60-minute callouts" has to point at the page that says it.
{BRAND} harvests the exact words from your own site and refuses to publish a
figure that is not there. Recombine two true statements into a third one nobody
said, and it flags it for your sign-off instead of quietly shipping it.</p>
<p>You get an <strong>evidence receipt</strong>: every claim beside the URL and
verbatim quote behind it — plus the ones needing sign-off, the ones blocked, and
the pages it could not read. Built for whoever signs the ad off and is
personally liable for it.</p>

<h2>It knows what will get rejected</h2>
<p>Before you paste anything anywhere, it checks the campaign against each
platform's published limits and hard floors:</p>
<ul>
<li>A LinkedIn campaign split two ways needs <strong>600</strong> people, not
300 — the minimum is per ad set. A 500-person audience creates both ad sets,
goes live, and delivers nothing, with no error anywhere.</li>
<li>A 6-second YouTube bumper records <strong>no views</strong> and builds
<strong>no remarketing list</strong>. A funnel planning to retarget its viewers
has no second stage and no warning.</li>
<li>A TikTok custom audience under <strong>1,000</strong> matched users cannot
be used at all.</li>
</ul>
<p>It separates "the platform will refuse this" from "this will be cut off",
because those need different reactions on different days — and it tells you what
it could <em>not</em> check, so an empty warning list never reads as a clean
bill of health.</p>

<h2>{len(specs)} platforms, held as dated facts</h2>
<p>{esc(names)}. Every character limit, aspect ratio and hard floor quoted from
the platform's own documentation with the date it was read.
<a href="/specs/">Read the specs</a>.</p>

<h2 id="get">Get it</h2>
<div class="panel">
<p><strong>Mac, signed and notarised.</strong> Runs locally. No account, no
server, nothing about your product leaves the machine when you use a local
model. Your API keys stay in your own config directory.</p>
<p class="src">Download link goes here once the build is published.</p>
</div>

<h2>What it deliberately does not do</h2>
<p>It does not make the image or the video. What it produces is a brief specific
enough to hand to a designer or a creative generator — if the asset is what you
need, buy one of those, and feed it this.</p>
<p>It does not predict performance. A "conversion score" on an ad that has never
run is a guess in the typography of a metric, and this tool does not publish
numbers it did not measure. That looks like a missing feature in a demo. It is
the reason to believe everything else it tells you.</p>
"""
    page(path="/", title=f"{BRAND} — the ad maker that proves its own claims",
         description=("Turns a product page into a complete ad campaign — strategy, "
                      "audiences, exclusions, copy and measurement — then traces every "
                      "claim to your site and checks it against each platform's real "
                      "limits before you spend anything."),
         body=body,
         schema={"@context": "https://schema.org", "@type": "SoftwareApplication",
                 "name": BRAND, "applicationCategory": "BusinessApplication",
                 "operatingSystem": "macOS",
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
              f'<div class="grid">{cards}</div></article>')


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
<p><a class="cta" href="/#get">Get {BRAND}</a>
<a class="cta ghost" href="/specs/">See the ad specs</a></p>
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

_ARTICLES = [
    (
        "linkedin-ad-set-not-delivering",
        "Your LinkedIn ad set is not delivering and there is no error",
        "LinkedIn needs 300 member accounts per ad set. Split an audience across "
        "two ad sets and you need 600. Below that it just does not run.",
        """
<p>LinkedIn states the minimum audience size required to run an ad set is
<strong>300 member accounts</strong>. That number is per ad set, which is the
part that catches people.</p>
<p>Split a 500-person audience into a two-cell test and you have created two ad
sets of roughly 250. Both are under the floor. Both were accepted at setup. The
campaign is live, the status is green, and nothing delivers.</p>
<h2>Why it is silent</h2>
<p>Nothing about this is an error. You built a valid campaign and asked for an
audience the platform cannot serve. On Meta, narrowing hurts delivery
gradually; on LinkedIn you cross a line and it stops.</p>
<h2>What to do</h2>
<ul>
<li>Multiply the floor by the number of cells before you design the test. Two
cells means 600, four means 1,200.</li>
<li>Check the forecast panel <em>before</em> writing creative — it is the step
that most often sends you back to the start.</li>
<li>Prefer two cells over four. B2B targeting stacks land near the floor fast.</li>
</ul>
<p>Read the full <a href="/specs/linkedin/">LinkedIn ad specs</a>, quoted with
sources.</p>
<p>{BRAND} checks this automatically: tell it the audience size and it works out
whether every cell clears the floor, and says so before you build anything.</p>
""".replace("{BRAND}", BRAND),
    ),
    (
        "youtube-bumper-remarketing",
        "Why your YouTube bumper campaign built no remarketing list",
        "Google states view counts need a video of 10+ seconds and remarketing "
        "lists need 12+. A 6-second bumper produces neither.",
        """
<p>The plan is sensible and very common: run cheap 6-second bumpers for reach,
then retarget everyone who saw one. It cannot work, and nothing tells you.</p>
<p>Google states that YouTube view counts are not incremented unless the video
ad is <strong>10 seconds or longer</strong>, and that building remarketing lists
or using YouTube Analytics requires <strong>12+ seconds</strong>.</p>
<h2>Two separate consequences</h2>
<ul>
<li><strong>Zero views.</strong> A bumper campaign reporting no views is not
broken. It is working exactly as documented.</li>
<li><strong>No second stage.</strong> The audience you planned to retarget was
never created, so the rest of the funnel has nothing to run against.</li>
</ul>
<h2>Decide the length first</h2>
<p>This is why video duration belongs at the top of a YouTube build, not at the
end. Everything else can be edited after the fact. Length cannot be fixed
without reshooting.</p>
<p>If anything downstream depends on retargeting viewers, the creative has to be
at least 12 seconds before you decide anything else.</p>
<p>See the <a href="/specs/youtube/">YouTube ad specs</a>, quoted with sources.</p>
""",
    ),
    (
        "ad-copy-truncation-vs-hard-limits",
        "The two different character limits every ad platform has",
        "One number gets your ad rejected. The other lets it run with the "
        "sentence cut in half. Most guides publish only one of them.",
        """
<p>Every ad field has two limits, and conflating them is why copy that "fit"
still reads as a fragment in the feed.</p>
<ul>
<li>The <strong>hard cap</strong> — past this, the upload is refused.</li>
<li>The <strong>visible limit</strong> — past this, it runs and gets truncated
behind a "see more" or an ellipsis.</li>
</ul>
<h2>They can be far apart</h2>
<p>LinkedIn's single image ad takes a headline of up to 200 characters and cuts
it at 70. Its introductory text takes 3,000 and cuts at 150. YouTube's in-feed
headline takes 100 characters but anything past 25 "may be shortened on some
devices".</p>
<p>So a 120-character headline is a <em>truncation</em> on LinkedIn and a flat
<em>rejection</em> on X, where the cap is 70. Same copy, different failure.</p>
<h2>The link tax on X</h2>
<p>X states that each link used reduces the character count by 23, "electing 257
characters for X copy". Every ad has a destination, so 257 is the real budget
and anything written to 280 will not fit.</p>
<h2>Write to the visible number</h2>
<p>A headline that fits the cap but gets cut off mid-word is a worse ad than a
shorter one. Write to the visible limit and keep the cap as headroom.</p>
<p><a href="/specs/">All eight platforms, both numbers, with sources.</a></p>
""",
    ),
    (
        "pinterest-description-invisible",
        "Nobody reads your Pinterest description",
        "Pinterest states descriptions do not appear in the feed, in search, or "
        "when a Pin is viewed up close. They feed the ranking algorithm.",
        """
<p>Pinterest's own specification states that descriptions "do not appear when
viewing the Pin in the home feed or search feed" and "do not appear for ads when
viewed up close" — and separately that "descriptions are used by our algorithm
to determine relevance for delivery".</p>
<p>It is a retrieval field wearing the clothes of a copy field.</p>
<h2>What follows</h2>
<ul>
<li>Persuasion belongs in the image and in the <strong>first 40 characters</strong>
of the title. The title field takes 100, but only about 40 show in feed — 30 for
Chinese, Japanese, Korean and Arabic.</li>
<li>Writing 800 characters of sales copy in the description is invisible work.</li>
<li>A test that varies the description is testing something no user will see.
Write it to be <em>found</em>, not to be read.</li>
</ul>
<h2>And 2:3, not square</h2>
<p>Pinterest warns that Pins with an aspect ratio greater than 2:3 "might get cut
off in people's feeds" — the opposite of the square-is-safe habit every other
platform trains.</p>
<p>See the <a href="/specs/pinterest/">Pinterest ad specs</a>, quoted with sources.</p>
""",
    ),
    (
        "tiktok-targeting-and-or",
        "Why your TikTok ad group will not spend",
        "Selections OR within a dimension and AND across them — the opposite of "
        "the intuition Meta trains. Plus a 1,000-user floor on custom audiences.",
        """
<p>TikTok states that "selections within the same dimension operate on OR logic"
and "selections across dimensions operate with AND logic".</p>
<p>So adding a second interest <em>widens</em> your audience, and adding a second
dimension <em>narrows</em> it. People arriving from Meta usually assume the
reverse, stack four dimensions to be precise, and produce an ad group too thin
to spend.</p>
<h2>The custom audience floor</h2>
<p>TikTok requires <strong>1,000 total matched users</strong> in a custom
audience before it can be used in an ad group. A small business's customer list
frequently will not qualify after matching — and TikTok notes the matched list
is always smaller than what you uploaded.</p>
<h2>Two things this means</h2>
<ul>
<li>Do not quote your upload count as your audience size. It is not.</li>
<li>If the list is small, use interest or behaviour targeting instead. TikTok's
useful signal is behavioural — what someone watched, liked and shared recently —
not declared attributes. There is no job title here.</li>
</ul>
<p>See the <a href="/specs/tiktok/">TikTok ad specs</a>, quoted with sources.</p>
""",
    ),
    (
        "special-ad-categories",
        "Special ad categories: when your targeting is illegal, not just wrong",
        "Housing, employment and credit ads carry legal obligations that survive "
        "any platform's interface. Excluding by postcode is still discrimination.",
        """
<p>If your ad is about housing, employment, or credit, the rules are not the
platform's preferences. They are law, and the platform's category declaration is
how you comply with it — not the whole of it.</p>
<h2>Declare the category</h2>
<p>Meta calls this a Special Ad Category. Declaring it removes targeting options
that would otherwise be available, which is the point: age and gender targeting
on job ads is unlawful under the ADEA and Title VII, and targeting housing ads
by age, gender or postcode runs into the Fair Housing Act. Credit
discrimination is prohibited by the Equal Credit Opportunity Act.</p>
<h2>Proxies count</h2>
<p>The mistake that survives the declaration is the proxy exclusion. An
interest, a postcode, a language, a "lookalike" seeded on a skewed list — each
can produce the same outcome as excluding a protected characteristic directly.
<strong>Intent is not the test.</strong> The effect is.</p>
<h2>In the UK and EU</h2>
<p>The Equality Act 2010 and equivalent EU directives land in the same place by
a different route, and financial promotions carry their own regime: under FSMA
section 21, communicating an unapproved financial promotion is a criminal
offence, not a compliance ticket.</p>
<div class="panel warn"><p style="margin:0">This is a plain-English summary of
why the controls exist, not legal advice. If you are running these ads, the
person who signs them off should be someone qualified to.</p></div>
<p>{BRAND} runs a compliance pre-flight over these categories on every campaign
and renders the obligations above the build steps — before the money, not
after.</p>
""".replace("{BRAND}", BRAND),
    ),
]
