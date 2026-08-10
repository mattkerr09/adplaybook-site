"""The /learn/ articles.

Split out of content.py once there were more than a handful. Two rules hold
here and both came out of auditing the first six with the sibling project's
aitell.py:

**Contractions.** The first batch scored 0.00 contractions per thousand words.
Nobody writes that way. It is the single loudest signal that prose came out of
a model, and it costs nothing to fix.

**Em-dashes.** The same batch ran at 17.6 per thousand against a target under
6. An em-dash is the default joint an LLM reaches for, and a page full of them
reads wrong even to someone who cannot say why. Most of them want to be a
comma, a colon, or a full stop.

Every figure in here is quoted from the platform's own documentation and was
read on 2026-08-10. Where a platform publishes nothing, these say so rather
than repeating a number from a blog.
"""

from __future__ import annotations

BRAND = "AdPlaybook"

ARTICLES = [
    (
        "linkedin-ad-set-not-delivering",
        "Your LinkedIn ad set isn't delivering and there's no error",
        "LinkedIn needs 300 member accounts per ad set. Split an audience across "
        "two ad sets and you need 600. Below that it simply doesn't run.",
        """
<p>LinkedIn states the minimum audience size required to run an ad set is
<strong>300 member accounts</strong>. That's per ad set, which is the part that
catches people out.</p>
<p>Split a 500-person audience into a two-cell test and you've just created two
ad sets of roughly 250. Both are under the floor. Both were accepted at setup.
The campaign is live, the status is green, and nothing delivers.</p>
<h2>Why it's silent</h2>
<p>None of this is an error. You built a valid campaign and asked for an
audience the platform can't serve. On Meta, narrowing hurts delivery gradually.
On LinkedIn you cross a line and it stops.</p>
<h2>What to do</h2>
<ul>
<li>Multiply the floor by the number of cells before you design the test. Two
cells means 600. Four means 1,200.</li>
<li>Check the forecast panel <em>before</em> writing creative. It's the step
that most often sends you back to the start.</li>
<li>Prefer two cells over four. B2B targeting stacks land near the floor fast.</li>
</ul>
<p>Full <a href="/specs/linkedin/">LinkedIn ad specs</a>, quoted with sources.</p>
""",
    ),
    (
        "youtube-bumper-remarketing",
        "Why your YouTube bumper campaign built no remarketing list",
        "Google states view counts need a video of 10+ seconds and remarketing "
        "lists need 12+. A 6-second bumper produces neither.",
        """
<p>The plan is sensible and very common. Run cheap 6-second bumpers for reach,
then retarget everyone who saw one. It can't work, and nothing tells you.</p>
<p>Google states that YouTube view counts aren't incremented unless the video ad
is <strong>10 seconds or longer</strong>, and that building remarketing lists or
using YouTube Analytics needs <strong>12+ seconds</strong>.</p>
<h2>Two separate consequences</h2>
<ul>
<li><strong>Zero views.</strong> A bumper campaign reporting no views isn't
broken. It's working exactly as documented.</li>
<li><strong>No second stage.</strong> The audience you planned to retarget was
never created, so the rest of the funnel has nothing to run against.</li>
</ul>
<h2>Decide the length first</h2>
<p>This is why video duration belongs at the top of a YouTube build rather than
the end. Everything else can be edited afterwards. Length can't be fixed without
reshooting.</p>
<p>If anything downstream depends on retargeting viewers, the creative needs to
be at least 12 seconds before you decide anything else.</p>
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
<li>The <strong>hard cap</strong>. Past this, the upload is refused.</li>
<li>The <strong>visible limit</strong>. Past this it runs, and gets truncated
behind a "see more" or an ellipsis.</li>
</ul>
<h2>They can sit a long way apart</h2>
<p>LinkedIn's single image ad takes a headline of up to 200 characters and cuts
it at 70. Its introductory text takes 3,000 and cuts at 150. YouTube's in-feed
headline takes 100 but anything past 25 "may be shortened on some devices".</p>
<p>So a 120-character headline is a <em>truncation</em> on LinkedIn and a flat
<em>rejection</em> on X, where the cap is 70. Same copy, different failure.</p>
<h2>The link tax on X</h2>
<p>X states that each link used reduces the character count by 23, "electing 257
characters for X copy". Every ad has a destination, so 257 is your real budget
and anything written to 280 won't fit.</p>
<h2>Write to the visible number</h2>
<p>A headline that fits the cap but gets cut off mid-word is a worse ad than a
shorter one. Write to the visible limit and treat the cap as headroom.</p>
<p><a href="/specs/">All eight platforms, both numbers, with sources.</a></p>
""",
    ),
    (
        "pinterest-description-invisible",
        "Nobody reads your Pinterest description",
        "Pinterest states descriptions don't appear in the feed, in search, or "
        "when a Pin is viewed up close. They feed the ranking algorithm.",
        """
<p>Pinterest's own specification states that descriptions "do not appear when
viewing the Pin in the home feed or search feed" and "do not appear for ads when
viewed up close". Separately, that "descriptions are used by our algorithm to
determine relevance for delivery".</p>
<p>It's a retrieval field wearing the clothes of a copy field.</p>
<h2>What follows from that</h2>
<ul>
<li>Persuasion belongs in the image and in the <strong>first 40 characters</strong>
of the title. The title field takes 100, but only about 40 show in feed, and 30
for Chinese, Japanese, Korean and Arabic.</li>
<li>Writing 800 characters of sales copy in the description is invisible work.</li>
<li>A test that varies the description is testing something no user will see.
Write it to be <em>found</em>, not to be read.</li>
</ul>
<h2>And 2:3, not square</h2>
<p>Pinterest warns that Pins with an aspect ratio greater than 2:3 "might get cut
off in people's feeds". That's the opposite of the square-is-safe habit every
other platform trains into you.</p>
<p>See the <a href="/specs/pinterest/">Pinterest ad specs</a>, quoted with sources.</p>
""",
    ),
    (
        "tiktok-targeting-and-or",
        "Why your TikTok ad group won't spend",
        "Selections OR within a dimension and AND across them, which is the "
        "opposite of what Meta teaches. Plus a 1,000-user floor on custom audiences.",
        """
<p>TikTok states that "selections within the same dimension operate on OR logic"
and "selections across dimensions operate with AND logic".</p>
<p>So adding a second interest <em>widens</em> your audience, and adding a second
dimension <em>narrows</em> it. People arriving from Meta usually assume the
reverse, stack four dimensions to be precise, and build an ad group too thin to
spend.</p>
<h2>The custom audience floor</h2>
<p>TikTok requires <strong>1,000 total matched users</strong> in a custom
audience before it can be used in an ad group. A small business's customer list
frequently won't qualify after matching, and TikTok notes the matched list is
always smaller than what you uploaded.</p>
<h2>Two things that follow</h2>
<ul>
<li>Don't quote your upload count as your audience size. It isn't.</li>
<li>If the list is small, use interest or behaviour targeting instead. TikTok's
useful signal is behavioural, meaning what someone watched, liked and shared
recently. There's no job title here.</li>
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
<p>If your ad is about housing, employment, or credit, the rules aren't the
platform's preferences. They're law, and the platform's category declaration is
how you comply with part of it, not the whole of it.</p>
<h2>Declare the category</h2>
<p>Meta calls this a Special Ad Category. Declaring it removes targeting options
that would otherwise be available, which is the point. Age and gender targeting
on job ads is unlawful under the ADEA and Title VII. Targeting housing ads by
age, gender or postcode runs into the Fair Housing Act. Credit discrimination is
prohibited by the Equal Credit Opportunity Act.</p>
<h2>Proxies count</h2>
<p>The mistake that survives the declaration is the proxy exclusion. An interest,
a postcode, a language, a lookalike seeded on a skewed list: each can produce the
same outcome as excluding a protected characteristic directly.
<strong>Intent isn't the test.</strong> The effect is.</p>
<h2>In the UK and EU</h2>
<p>The Equality Act 2010 and equivalent EU directives land in the same place by a
different route. Financial promotions carry their own regime on top: under FSMA
section 21, communicating an unapproved financial promotion is a criminal
offence, not a compliance ticket.</p>
<div class="box warn"><p style="margin:0">This is a plain-English summary of why
the controls exist. It isn't legal advice. If you're running these ads, the
person signing them off should be someone qualified to.</p></div>
<p>{BRAND} runs a compliance pre-flight over these categories on every campaign
and renders the obligations above the build steps, before the money rather than
after it.</p>
""".replace("{BRAND}", BRAND),
    ),
    (
        "x-link-costs-23-characters",
        "Your X ad has 257 characters, not 280",
        "X states every link costs 23 characters. Every ad has a destination, so "
        "copy written to the advertised limit doesn't fit.",
        """
<p>X's creative specification is blunt about it: "280 characters. (Note: each
link used reduces character count by 23 characters, electing 257 characters for X
copy.)"</p>
<p>Every ad this side of a brand-awareness buy has a destination. So 257 is the
number, and a variant written to 280 gets rejected or truncated at the point you
least want to find out.</p>
<h2>Hashtags come out of the same budget</h2>
<p>X specifies a hashtag at "21 characters, including the hashtag character".
That's counted against your 257 too. Two hashtags and a link leave you about 215
characters of actual sentence.</p>
<h2>The headline is a separate, tighter field</h2>
<p>The website card title takes 70 characters. X notes that "up to two lines of
text are rendered on the card title", with anything beyond truncated by an
ellipsis, and suggests keeping it to 50 to be safe across devices.</p>
<h2>What this changes about testing</h2>
<p>X advises keeping 3 to 5 creative options in rotation rather than one tightly
isolated variable. Combined with no minimum campaign spend, the cheap move here
is more creative variety rather than a precisely controlled matrix. That's a
different philosophy from Meta's, and worth deciding on deliberately instead of
importing your Meta habits.</p>
<p>See the <a href="/specs/x/">X ad specs</a>, quoted with sources.</p>
""",
    ),
    (
        "meta-lookalike-minimum-source",
        "Your Meta lookalike needs 100 people from one country",
        "Meta requires at least 100 people from a single country in the source "
        "audience. A list spread across five markets can fail while looking big enough.",
        """
<p>Meta states that a lookalike source audience needs <strong>at least 100
people from one country</strong>. The country part is what surprises people.</p>
<p>A 300-person customer list sounds comfortably over the line. Spread it across
the UK, Ireland, Germany, France and Spain at 60 apiece and no single country
clears 100, so there's nothing to build from.</p>
<h2>Bigger seeds aren't automatically better</h2>
<p>A lookalike is only as good as what it's modelled on. Seeding from everyone
who ever bought gives you a model of your average customer, including the ones
who refunded. Seeding from your best 200 customers usually beats seeding from all
5,000, and it's the version most people never try.</p>
<h2>The proxy-discrimination trap</h2>
<p>If the campaign is about housing, employment or credit, a lookalike seeded on
a skewed customer list can reproduce a protected-characteristic exclusion without
anyone choosing one. The declaration doesn't save you from that, because the test
is the effect and not the intent. Our note on
<a href="/learn/special-ad-categories/">special ad categories</a> covers the rest.</p>
<p>See the <a href="/specs/meta/">Meta ad specs</a>, quoted with sources.</p>
""",
    ),
    (
        "audience-floors-by-platform",
        "The minimum audience size on every major ad platform",
        "Four platforms publish a hard floor. Below it, campaigns are accepted, "
        "go live, and deliver nothing. Here's each one with its source.",
        """
<p>Several platforms enforce a minimum below which an ad set simply won't run.
None of them raise an error at setup. The campaign is created, the status looks
healthy, and there's no delivery.</p>
<h2>What each platform publishes</h2>
<table>
<thead><tr><th>Platform</th><th>Floor</th><th>Applies to</th></tr></thead>
<tbody>
<tr><td><a href="/specs/linkedin/">LinkedIn</a></td><td><strong>300</strong> member accounts</td>
<td>Per ad set. Split a test two ways and you need 600 in total.</td></tr>
<tr><td><a href="/specs/tiktok/">TikTok</a></td><td><strong>1,000</strong> matched users</td>
<td>Custom audiences. Below this the audience can't be used at all.</td></tr>
<tr><td><a href="/specs/meta/">Meta</a></td><td><strong>100</strong> people from one country</td>
<td>Lookalike source audiences.</td></tr>
<tr><td><a href="/specs/x/">X</a></td><td>No minimum spend stated</td>
<td>X states there's no minimum campaign spend, so small tests are genuinely possible.</td></tr>
</tbody>
</table>
<h2>The arithmetic people skip</h2>
<p>A floor that applies per ad set multiplies by the number of cells in your
test. This is the single most common way a well-designed experiment produces
nothing: the audience was fine, the split wasn't.</p>
<p>Work it out before you write creative, not after. On LinkedIn especially, the
forecast panel is the step that most often sends you back to the start.</p>
<h2>What isn't on this list</h2>
<p>Google, Pinterest, Reddit and YouTube either don't publish a comparable floor
or didn't state one on the pages we read. Absence here means we couldn't verify
one, not that none exists. Each <a href="/specs/">spec page</a> lists what we
could and couldn't check.</p>
""",
    ),
    (
        "video-length-by-platform",
        "How long should an ad video be on each platform",
        "Every platform publishes a maximum and a recommendation, and they're "
        "nowhere near each other. Two also have thresholds that break your funnel.",
        """
<p>Maximums are ceilings, not targets, and treating them as targets is how you
end up with a two-minute ad nobody finishes. Here's what each platform actually
publishes.</p>
<table>
<thead><tr><th>Platform</th><th>Recommended</th><th>Maximum</th></tr></thead>
<tbody>
<tr><td><a href="/specs/tiktok/">TikTok</a></td><td>Not stated on the in-feed page</td><td>Up to 10 minutes</td></tr>
<tr><td><a href="/specs/pinterest/">Pinterest</a></td><td>6 to 15 seconds</td><td>15 minutes, minimum 4 seconds</td></tr>
<tr><td><a href="/specs/x/">X</a></td><td>15 seconds or less</td><td>2 minutes 20 seconds</td></tr>
<tr><td><a href="/specs/youtube/">YouTube</a></td><td>15 to 20s for awareness, 2 to 3 min for consideration</td><td>Varies by format</td></tr>
</tbody>
</table>
<h2>Two YouTube thresholds that aren't about attention</h2>
<p>Google states that view counts aren't incremented below <strong>10
seconds</strong>, and that remarketing lists and YouTube Analytics need
<strong>12+ seconds</strong>. These aren't performance guidance. They decide
whether you get any data at all, so a 6-second bumper builds no audience for
whatever you planned to run next.</p>
<h2>The first five seconds are the only ones you're guaranteed</h2>
<p>A skippable in-stream ad can be skipped after 5 seconds. Whatever the total
length, everything the ad must communicate has to survive being abandoned at
five. X reaches a similar conclusion from a different direction: it advises 6 to
15 second videos with captions and prominent branding.</p>
<h2>File size is a separate trap</h2>
<p>X allows 1GB and then says to keep files under 30MB for performance.
Pinterest allows 2GB. Those aren't invitations. Upload the ceiling and you'll
watch delivery suffer for a reason that never appears in any report.</p>
""",
    ),
    (
        "why-square-isnt-always-safe",
        "Square isn't the safe default on every platform",
        "Most platforms train you to make everything 1:1. Pinterest cuts anything "
        "taller than 2:3, and vertical wins the most screen on several others.",
        """
<p>Square is the habit because it's the safest single answer on Meta. Carry it
everywhere and you'll waste most of the screen on half the platforms you buy.</p>
<h2>Pinterest inverts it</h2>
<p>Pinterest recommends <strong>2:3</strong>, or 1000 x 1500 pixels, and warns
that "Pins with an aspect ratio greater than 2:3 might get cut off in people's
feeds". Taller isn't better here, it's cropped. Square is allowed and gives away
the vertical space the feed is built around.</p>
<h2>X says square and vertical take the same space</h2>
<p>X's guidance is unusually direct: "1:1 is recommended as it will always render
as square on desktop and mobile, timeline and profile. This and 9:16 (vertical)
will take up the same amount of real estate, which is more than 16:9." So 16:9
is the one costing you.</p>
<h2>TikTok is vertical or nothing</h2>
<p>TikTok recommends 9:16 at 540 x 960 or larger. Horizontal and square are
accepted, and both look like an import from somewhere else, which is the one
thing the platform reliably punishes.</p>
<h2>LinkedIn's numbers are per-format</h2>
<p>The single image ad recommends 1.91:1 at 1200 x 628, with square and 4:5 also
supported. The carousel is 1:1 at 1080 x 1080, and LinkedIn notes those images
get "scaled to 312 x 312px", so anything that has to be legible needs to survive
being shown at about a third of a business card.</p>
<p>Every ratio above is on the <a href="/specs/">spec pages</a> with its source
and the date we read it.</p>
""",
    ),
    (
        "tiktok-captions-no-links-hashtags",
        "TikTok ad captions can't contain links, @ or hashtags",
        "TikTok states the caption supports none of them. Copy built around a "
        "hashtag or an @mention arrives broken, and the spec page states no character count.",
        """
<p>TikTok's in-feed specification states the ad caption is "displayed in white
with a uniform font that can't be customized" and "does not support any clickable
links, symbols (@), or hashtags".</p>
<p>That rules out a lot of copy patterns people bring from organic. A caption
built around a branded hashtag, or one that @mentions a creator, doesn't
degrade gracefully. It just reads as broken.</p>
<h2>There's no published character count</h2>
<p>Worth stating plainly, because everyone else publishes one: TikTok's own
in-feed specification page states <strong>no character limit for ad text</strong>.
We checked it twice. The 100-character figure that appears in most guides
doesn't appear in TikTok's documentation, so we don't assert it either.</p>
<p>Write the caption short because it sits over video and truncates behind a
"See more", not because a specific number has been published.</p>
<h2>Spark Ads take the caption from the post</h2>
<p>A Spark Ad promotes an organic post that already exists, and TikTok states its
captions are "extracted directly from the organic video captions", with a maximum
of four lines displayed. So the copy decision happens when the post is written,
not in Ads Manager. Choosing Spark after writing ad copy means throwing that copy
away, which is why that decision belongs near the top of a TikTok build.</p>
<p>See the <a href="/specs/tiktok/">TikTok ad specs</a>, quoted with sources.</p>
""",
    ),
    (
        "google-responsive-search-ads-testing",
        "You can't run a clean A/B test inside a responsive search ad",
        "Google recombines your headlines before anyone sees them. A one-variable "
        "matrix inside a single RSA isn't attributable to anything.",
        """
<p>Responsive search ads take up to 15 headlines and 4 descriptions and assemble
combinations at auction time. That's the feature. It's also why the testing habit
people bring from Meta produces numbers that can't be read.</p>
<h2>The problem with a one-axis matrix</h2>
<p>On Meta you can hold everything constant and change one line, because the ad
that serves is the ad you built. In an RSA, the headline you're testing appears
alongside a different second headline each time. When performance moves, you
can't attribute it to the line you changed.</p>
<h2>What to do instead</h2>
<ul>
<li>Test at the <strong>ad</strong> level, not the asset level. Two RSAs with
genuinely different angles beat fifteen headlines in one.</li>
<li>Use asset performance ratings for what they are: a signal about which assets
are being chosen, not a controlled result.</li>
<li>Pin sparingly. Pinning restores control and gives up most of the reason to
use the format.</li>
</ul>
<h2>Negative keywords are the other half</h2>
<p>Search is the one place where deciding who <em>not</em> to reach matters as
much as the targeting. Negatives don't close-match, so plurals, misspellings and
variants each need their own entry. A negative for "free" won't block "freely".</p>
<p>{BRAND} generates negative keywords rather than leaving them to you, and only
for platforms that actually have search terms to exclude. See the
<a href="/specs/google/">Google Ads specs</a>.</p>
""".replace("{BRAND}", BRAND),
    ),
    (
        "what-an-unsubstantiated-claim-costs",
        "The claim in your ad you can't actually back up",
        "Ad platforms and regulators both work backwards from the claim to the "
        "evidence. If the sentence isn't on your own site, you're the one holding it.",
        """
<p>Most ad copy that gets an account in trouble isn't a lie. It's a recombination:
two true statements from different pages, merged into a third thing nobody
actually said.</p>
<p>Your site says callouts are answered within 60 minutes. Another page says
you're Gas Safe registered. The ad says "Gas Safe engineers at your door in 60
minutes". Both halves are true. The sentence is new, and nobody verified it.</p>
<h2>Why this is the expensive kind</h2>
<p>A rejected ad is cheap, because you find out immediately. A claim that runs
for six weeks and then gets challenged is expensive, because by then it's in
your creative library, your landing page and your sales calls.</p>
<p>In regulated categories it's worse than expensive. Under FSMA section 21,
communicating an unapproved financial promotion is a criminal offence rather than
a compliance ticket, and the person who approved it is the person on the hook.</p>
<h2>The question a reviewer actually asks</h2>
<p>Not "is this good copy". It's "show me where this sentence comes from". That's
answerable in about a minute if you kept the trail, and it's a research project
if you didn't.</p>
<h2>What {BRAND} does about it</h2>
<p>Every factual claim has to resolve to a verbatim quote at a URL on your own
site. Figures that appear nowhere in your copy get blocked outright. Sentences
that recombine two true statements get flagged for your sign-off rather than
shipped quietly, because you're the one who has to stand behind the combined
version.</p>
<p>You get an evidence receipt listing every claim next to the exact quote
supporting it, plus the ones needing sign-off, the ones that were blocked, and
the pages the crawler couldn't read. A receipt that lists only the wins isn't
worth signing.</p>
""".replace("{BRAND}", BRAND),
    ),
]
