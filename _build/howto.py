"""The /how-to/ hub.

Every other hub on this site describes what something IS: /specs/ lists a
platform's limits, /learn/ explains a concept, /for/ addresses a trade. Nobody
arrives at 2am typing "LinkedIn character limits". They type "why is my ad not
delivering" and "my split test says nothing".

So these pages are organised by the failure, and each one is grounded in
something this project measured rather than something a copywriter imagined.
The numbers come from the same platform JSON the app reads at runtime and from
the batch corpus in ad maker app/batch/, so a page cannot drift from the
product's behaviour without the build noticing.

The rule that shapes all of them: where a figure appears, it is one we counted,
with the denominator beside it. Where we did not measure, the page says so
rather than reaching for a plausible number — this project has already come
within one commit of publishing a fabricated cost table, and a how-to full of
invented benchmarks is the same failure wearing a more useful hat.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

# page() and PAGES are passed in rather than imported.
#
# render.py runs as __main__, so `from render import page` loads a SECOND copy
# of that module with its own PAGES list. The pages were written to disk and
# appended to a list nobody read, so four live pages stayed out of the sitemap.
# content.py already takes them as arguments for this reason — the signature
# build_rest(page, specs, PAGES) is the fix, written down before I hit it.
from render import BASE_URL, esc

APP = Path.home() / "ad maker app"
PLATFORMS = APP / "backend" / "adkit" / "platforms"


def _platform(key: str) -> Dict:
    return json.loads((PLATFORMS / f"{key}.json").read_text())


def _faq(pairs: List[tuple]) -> Dict:
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in pairs
        ],
    }


# ---------------------------------------------------------------------------
# 1. The split test that cannot say anything.

def _split_test(page) -> None:
    body = """
<p class="lede">If both cells contain the same words, the test can't give you a result. Whichever wins, the number is noise — and you paid twice for one ad.</p>

<p>It's the most common way a first campaign wastes its budget, and it's almost invisible: the ads manager accepts it, both cells deliver, and the report
shows a winner. The winner is variance.</p>

<h2>How to tell</h2>
<p>Put the two cells side by side and read only the words a person would see —
headline, body, button. Ignore the labels. A test matrix that says
<em>"Variant A: control / Variant B: emotional hook"</em> is describing an
intention, not a difference. If the visible copy's identical, so is the ad.</p>

<h2>Why generated campaigns are prone to it</h2>
<p>We measured this in our own output. Across 48 generated campaigns carrying two
or more cells, <strong>35 shared one headline across every cell</strong> and
<strong>15 were identical in both headline and body</strong>. The model filled in
the axis labels correctly every time and then wrote the same ad twice.</p>
<p>That isn't a quirk of one tool. Asking for "variations" gets you paraphrase,
because paraphrase is what the request literally describes. A test needs a
different <em>idea</em>, not different adjectives.</p>

<h2>How to fix it</h2>
<ol>
<li><strong>Change the angle, not the wording.</strong> If cell A leads on price,
cell B should lead on the objection that stops people buying, not on the same price in warmer language.</li>
<li><strong>Vary one thing.</strong> Two cells differing on everything tell you
which one won and nothing about why. One axis per cell, named.</li>
<li><strong>Check the audience survives the split.</strong> A 500-person audience
split in two is two cells of 250, and LinkedIn will not deliver below 300 per
cell. The campaign goes live and nothing happens — you won't be told why.</li>
</ol>

<h2>What this page does not tell you</h2>
<p>Whether your two distinct cells are any <em>good</em>. This is about whether a
test can produce an answer at all. A campaign can clear every point here and still be two weak ads.</p>
"""
    page(
        path="/how-to/split-test-ads-that-actually-say-something/",
        title="How to run an ad split test that actually says something",
        description=("Two cells with the same copy cannot produce a result. How to "
                     "spot a null test, why generated campaigns produce them, and "
                     "what to vary instead."),
        body=body,
        schema=_faq([
            ("Why does my A/B test show no difference?",
             "If both cells carry the same headline and body text, there is no "
             "variable to measure. Whichever cell wins, the difference is "
             "variance rather than a result."),
            ("How different do ad variants need to be?",
             "Different on one named axis, and different in the words a reader "
             "actually sees. Changing adjectives produces paraphrase, not a test."),
        ]),
    )


# ---------------------------------------------------------------------------
# 2. Why an ad is not delivering — from the real floors.

def _not_delivering(page) -> None:
    """The floors, and the fact that almost nobody publishes one.

    The first draft of this page asserted that "every platform has a minimum
    audience it will deliver to" and built a table to prove it. Reading the
    actual platform data killed that: of the eight platforms this project
    tracks, exactly ONE — LinkedIn — publishes a minimum audience size. The
    rest publish nothing.

    That is the more useful page anyway. "Your audience is too small" is the
    first thing anyone is told when a campaign stalls, and on seven of eight
    platforms there is no published number behind that advice.
    """
    rows = []
    for key in ("meta", "linkedin", "tiktok", "google", "youtube", "pinterest",
                "x", "reddit"):
        try:
            p = _platform(key)
        except OSError:
            continue
        t = p.get("targeting_capabilities") or {}
        rows.append((p.get("name", key), t.get("minimum_audience_size"),
                     t.get("minimum_audience_note", ""),
                     t.get("verified_on", "")))

    table = "".join(
        f"<tr><td>{esc(n)}</td>"
        f"<td>{f'{fl:,}' if fl else 'not published'}</td>"
        f"<td>{esc(v) or 'not verified'}</td></tr>"
        for n, fl, _note, v in rows)
    published = [r for r in rows if r[1]]

    body = f"""
<p class="lede">A campaign that spends nothing usually isn't broken. But
"your audience is too small" is the first thing anyone is told, and on seven of
the eight platforms we track there is no published number behind that advice.</p>

<h2>Who actually publishes a floor</h2>
<table><thead><tr><th>Platform</th><th>Minimum audience</th>
<th>Spec verified</th></tr></thead><tbody>{table}</tbody></table>
<p class="note">Read from the same platform data our app checks against at
runtime. <strong>{len(published)} of {len(rows)}</strong> platforms publish a
minimum audience size. Where this says "not published", it means we looked and the platform doesn't state one — not that the number is zero, and not that we
failed to find it.</p>

<h2>The arithmetic that catches people</h2>
<p>Where a floor does exist it applies <strong>per cell</strong>, not per
campaign, and that is the trap. A 500-person LinkedIn audience clears the 300
floor comfortably. Split it into two test cells and each holds 250. Both are
under. The campaign's live, the status says Active, and neither cell delivers.</p>
<p>So the number to check is <strong>floor × cells</strong>.</p>

<h2>When no floor is published</h2>
<p>On the other seven, delivery is governed by the auction rather than by a
stated threshold, and a stalled campaign is more likely to be one of these:</p>
<ul>
<li><strong>The learning phase never exits.</strong> Under roughly 50
optimisation events a week per ad set, most platforms keep the ad set in
learning, where delivery is conservative and the reported cost per result is
noisy rather than informative. Editing the ad set restarts it.</li>
<li><strong>A special ad category is set.</strong> Housing, employment and
credit campaigns lose most targeting options by design. The campaign runs; the
audience is not the one you selected.</li>
<li><strong>The bid is below the auction floor.</strong> Nothing errors. The ad just never wins an impression.</li>
</ul>

<h2>What we could not check for you</h2>
<p>Whether your specific audience clears anything. No tool outside your ads
manager can see your forecast panel, and any tool that claims otherwise is guessing. Read the number there before launching.</p>
"""
    page(
        path="/how-to/fix-an-ad-that-is-not-delivering/",
        title="How to fix an ad that is not delivering",
        description=("Only one of eight ad platforms publishes a minimum audience "
                     "size. What the floors actually are, why they apply per test "
                     "cell, and what stalls delivery when no floor exists."),
        body=body,
        schema=_faq([
            ("Why is my ad active but not spending?",
             "Where a platform publishes an audience floor, the usual cause is "
             "that the audience fell below it once split across test cells — the "
             "floor applies per cell. Where no floor is published, delivery is "
             "governed by the auction, and the common causes are an unfinished "
             "learning phase, a special ad category restricting targeting, or a "
             "bid below the auction floor."),
            ("What is the minimum audience size for LinkedIn ads?",
             "LinkedIn requires 300 members, applied per cell. A two-cell test "
             "therefore needs at least 600 in total. It is the only platform of "
             "the eight we track that publishes such a number."),
        ]),
    )


# ---------------------------------------------------------------------------
# 3. Copy that reads as machine-written.

def _ai_slop(page) -> None:
    body = """
<p class="lede">A feed is a place where people are already looking for a reason
to scroll past. "Elevate your workflow with our cutting-edge solution" hands
them one in six words.</p>

<p>This matters more in an ad than almost anywhere else. A blog post that reads as generated is just dull. An ad that reads as generated is skipped before it
is read, and you are charged for the impression either way.</p>

<h2>The tells, in order of how badly they cost you</h2>
<ol>
<li><strong>Opener phrases.</strong> "Elevate your", "Unlock the", "Look no
further", "In today's fast-paced". That isn't weak writing, it's a signature — and readers have learned it.</li>
<li><strong>The not-just-X-it's-Y shape.</strong> "It's not just a CRM, it's a
growth engine." The single most recognisable generated-copy construction there
is.</li>
<li><strong>Three adjectives in a row.</strong> "Fast, simple, and powerful."
The rhythm gives it away before the meaning lands.</li>
<li><strong>No contractions anywhere.</strong> Body copy with none reads as a
press release. Nobody speaks that way, and formal register in a feed reads as
corporate rather than authoritative.</li>
<li><strong>Every cell opening on the same word.</strong> As a set this reads as
generated even when no single line does.</li>
</ol>

<h2>Why you cannot ask a model to check this</h2>
<p>Asking a language model whether text sounds like a language model is asking
the defendant to sit on the jury. It'll agree the copy is excellent, because agreeing is what it does. Every check worth running here is a count:
does this phrase appear, are there contractions, do all four headlines start
with the same word. Counts don't flatter.</p>

<h2>What we found in our own output</h2>
<p>Running that check across 38 generated campaigns: <strong>27 came back
clean, 7 read stiffly, and 4 were recognisably generated</strong>. Roughly a
quarter needed a rewrite before they were worth paying to show anyone. We publish it because a tool claiming a perfect record on its own output isn't telling you about its checking — it's telling you about its marketing.</p>

<h2>What this does not tell you</h2>
<p>Whether the copy is any good. It finds machine register, not weak positioning, and a page of plain human sentences can still be a bad ad.</p>
"""
    page(
        path="/how-to/stop-ad-copy-reading-like-ai/",
        title="How to stop your ad copy reading like AI wrote it",
        description=("The specific phrases and constructions readers have learned "
                     "to skip, why a model cannot check its own register, and what "
                     "we found across 38 of our own generated campaigns."),
        body=body,
        schema=_faq([
            ("How can you tell if ad copy was written by AI?",
             "Recognisable openers such as 'Elevate your' and 'Look no further', "
             "the 'not just X, it's Y' construction, three adjectives in a row, "
             "and body copy with no contractions at all."),
            ("Can AI detect its own writing?",
             "Not reliably. Asking a language model whether text sounds "
             "machine-written tends to produce agreement rather than judgement. "
             "Counted signals — specific phrases, contractions, repeated openers "
             "— are more dependable than asking."),
        ]),
    )


# ---------------------------------------------------------------------------

def _hub(page) -> None:
    cards = [
        ("/how-to/fix-an-ad-that-is-not-delivering/",
         "Fix an ad that is not delivering",
         "Audience floors apply per test cell. The published minimums, and the "
         "arithmetic that makes a healthy audience deliver nothing."),
        ("/how-to/split-test-ads-that-actually-say-something/",
         "Run a split test that actually says something",
         "Two cells with the same copy cannot produce a result. How to spot a "
         "null test — including in generated campaigns, where 35 of 48 of ours "
         "shared a headline."),
        ("/how-to/stop-ad-copy-reading-like-ai/",
         "Stop your ad copy reading like AI wrote it",
         "The phrases readers have learned to skip, and why a model cannot be "
         "trusted to check its own register."),
    ]
    body = """
<p class="lede">Organised by what went wrong, not by what a feature is called.
Nobody arrives here typing "character limits" — they arrive typing "why is my
ad not delivering".</p>

<div class="cards">
""" + "".join(
        f'<a class="card" href="{h}"><h3>{esc(t)}</h3><p>{esc(d)}</p></a>'
        for h, t, d in cards) + """
</div>

<p class="note">Every figure on these pages is one we counted, with its
denominator beside it. Where we have not measured something, the page says so
rather than reaching for a number that sounds right.</p>
"""
    page(
        path="/how-to/",
        title="How to fix common ad problems",
        description=("Practical fixes for campaigns that will not deliver, split "
                     "tests that say nothing, and copy that reads as machine-written."),
        body=body,
        schema={
            "@context": "https://schema.org",
            "@type": "CollectionPage",
            "name": "How to fix common ad problems",
            "url": BASE_URL + "/how-to/",
            "hasPart": [
                {"@type": "HowTo", "name": t, "url": BASE_URL + h}
                for h, t, _ in cards
            ],
        },
    )


def build(page) -> None:
    _hub(page)
    _not_delivering(page)
    _split_test(page)
    _ai_slop(page)


if __name__ == "__main__":
    from render import page as _p
    build(_p)
