"""Privacy, terms and contact.

DRAFT. Written by reading the product's source, not from a template, and **not
reviewed by a lawyer.** Nothing here should be treated as legal advice or as
approved copy. Every factual statement was checked against the code or the
signed artefact on the date in `EFFECTIVE`; the *legal* framing around those
facts has had no professional review at all.

Why this is a generator module and not three HTML files
-------------------------------------------------------
`render.py:page()` is the only thing that writes a page on this site, and three
separate gates in `check.py` fail a hand-written one: it is missing from
`sitemap.xml` (which is rebuilt from `PAGES` on every run), it has no
`name="last-modified"`, and any class it uses that is not in `render.py`'s CSS
string is a hard failure. A hand-written `/privacy/index.html` also *survives*
the rebuild — nothing deletes it — so the failure looks like success until the
sitemap silently drops it. So these go through `page()` like everything else,
and use only classes that already exist: `.crumb .lede .box .warn .ok .src
.muted .btn .ghost .pill .unchecked`.

Why the text is written rather than borrowed
--------------------------------------------
The obvious move is to paste a SaaS privacy policy. Every one of them describes
billing records, account identifiers, IP logs, cookies and a support ticket
system. AdPlaybook has none of those: no account, no server, no telemetry, no
payment mechanism anywhere in the repo. Publishing a policy that claims to
collect data this product cannot collect would put a fresh set of false
statements on the two pages a regulator reads first — on a site whose entire
argument is that every figure it prints is true.

So each claim below is sourced, the same way a spec page is:

* storage paths        `backend/adkit/llm.py:148-180`, `server.py:222-241`
* run state in memory  `backend/adkit/server.py:122` (`_RUNS`, never written)
* no telemetry         swept `backend/`, `ui/src/`, `ui/src-tauri/` on 2026-08-11
* crawler behaviour    `vendor/seo_engine/crawler.py:46,292-302`, `ingest.py:168`
* provider resolution  `git show 2636bed:backend/adkit/server.py:330,608`,
                       `providers.py:948,972,981,1020-1029`
* picker is inert      `ui/src/app.js:184` — binds "Use X" to `show('start')`
* openai.key unread    written `server.py:229-234`; resolved only from
                       `providers.py:977` (environment), so never read back
* landing-page fetch   `coherence.py:169,277-284`, `server.py:645-659`
* what v0.1.5 did      `git show dac347a:backend/adkit/llm.py:249-258` against
                       every call site — `brief.py:181`, `strategy.py:222`,
                       `generate.py:292`, `critique.py:260`, `coherence.py:285`
* signing identity     `codesign -dvvv` on `dist/AdPlaybook-0.1.23-arm64.dmg`
* zero MX records      `dig +short MX adplaybook.app` -> empty, 2026-08-12

Citations are pinned to `2636bed`, the commit v0.1.23 was built from, not to the
working tree. The tree is already on 0.1.24 and will move again; a page that
names a version has to cite that version's code.

Two things matter most.

First, `server.py:330` now reads `run.client = providers_mod.default_provider()`
— the first provider whose probe passes, in rank order: Outlier on `127.0.0.1`,
then OpenAI, then Anthropic. So the destination is no longer one name, and this
page names every outcome rather than the reassuring one. What did *not* get
fixed is the picker: `app.js:184` records nothing, so the choice is the
machine's.

Second, this page used to say v0.1.5 sent every run to Anthropic. **It sent
nothing.** `dac347a:llm.py:249-258` has no `tier` parameter and every call site
passes `tier=`, so CPython raised `TypeError` while binding the arguments —
before the method body, before any HTTP request. The page was confessing to a
disclosure that never happened.
"""

from __future__ import annotations

# The version these documents describe is the build the Download button serves.
# It was typed as v0.1.23 and went false the moment 0.1.89 was published.
# PRICE_USD, never a typed literal: the same $19 literal survived TWO price
# changes on crispvideo.app because every sweep fixed the published pages and
# not the generator that writes them.
from content import PRICE_USD, VERSION_TAG  # noqa: E402

import html
from typing import Any, Callable

BRAND = "AdPlaybook"
COMPANY = "Kerr &amp; Company LLC"
COMPANY_PLAIN = "Kerr & Company LLC"

#: Bumped by hand when the text changes, never generated from `date.today()`.
#: A policy whose "last updated" moves every time the site is rebuilt is
#: telling the reader something untrue about when it was last thought about.
#: One date per DOCUMENT, not one for the site. These were a single shared
#: constant until 2026-08-17, when the refund terms materially changed and
#: privacy did not. Bumping the shared value would have re-dated a page whose
#: text had not moved — the same untruth this constant exists to prevent,
#: pointed the other way.
TERMS_EFFECTIVE = "2026-08-18"   # "not for sale" retired: the site has charged $149 since before this
PRIVACY_EFFECTIVE = "2026-08-12"
EFFECTIVE = PRIVACY_EFFECTIVE    # legacy alias; prefer the explicit names

#: The only mailbox that has been confirmed to receive mail.
#:
#: `dig +short MX adplaybook.app` returns nothing — the domain has zero MX
#: records, so `support@adplaybook.app` would hard-bounce at the sending
#: server. An address that bounces is worse than no address: a payment
#: processor emails it during onboarding, it fails, and the application is
#: flagged. When MX records exist at Porkbun and a mailbox is live, change this
#: one constant and rebuild.
CONTACT_EMAIL = "matthew@kerrandcompanyholdings.com"

#: Street address, deliberately empty. A merchant-of-record application needs a
#: full registered address and inventing one is worse than shipping without it,
#: so the page renders city and state only until a real line goes here.
STREET_ADDRESS = ""
CITY_STATE = "Grand Rapids, Michigan, United States"

REPO = "https://github.com/mattkerr09/adplaybook-site"
RELEASES = f"{REPO}/releases"
ISSUES = f"{REPO}/issues"

#: Stamped into the source of every page this module writes. Not rendered: a
#: visible "no lawyer has read this" line on a live privacy policy undermines
#: the document for the exact reader it is written for. It belongs in the
#: source, where the person deciding whether to publish will see it.
DRAFT_NOTE = (
    "<!-- DRAFT. Assembled from the product's source code, and NOT REVIEWED BY "
    "A LAWYER. The facts are cited in _build/legal.py; the legal framing around "
    "them has had no professional review. Do not treat as approved copy. -->"
)


def esc(s: Any) -> str:
    return html.escape(str(s), quote=True)


def _address_html() -> str:
    if STREET_ADDRESS:
        return f"{esc(STREET_ADDRESS)}<br>{esc(CITY_STATE)}"
    return esc(CITY_STATE)


def build(page: Callable) -> None:
    _privacy(page)
    _terms(page)
    _contact(page)


# ---------------------------------------------------------------------------
# /privacy/
# ---------------------------------------------------------------------------

def _privacy(page: Callable) -> None:
    desc = ("What AdPlaybook sends and where it sends it, named destination by "
            "named destination, for the build you can download today — including "
            "which steps leave your Mac, which do not, and why you do not get to "
            "choose.")

    body = f"""{DRAFT_NOTE}
<article>
<p class="crumb">Privacy</p>
<h1>What this sends, and where</h1>
<p class="lede">{esc(desc)}</p>

<div class="box ok">
<p style="margin:0"><span class="pill checked">last changed {EFFECTIVE}</span>
Checked against the source of the build behind the Download button, not against
a template. Where the app and this page could disagree, the app is the fact and
this page is the bug.</p>
</div>

<h2>The short version</h2>
<p>There is no account, no server of ours, and no telemetry. Nothing is reported
back to {COMPANY}, because there is nowhere for it to be reported to. We hold no
data about you at all, so there is nothing for you to ask us to delete.</p>
<p>One step is different, and it is the one that matters. The writing is done by
a model, and <strong>which model — and therefore where your text goes — is
settled by your machine, not by you.</strong> If Outlier is answering here and
has issued a key this app can read, the writing happens on <code>127.0.0.1</code>
and nothing about your product leaves this Mac. If it is not, the text harvested
from your site, your product details, every draft ad, and up to 3,000 characters
of any landing page you point the ad at go over the internet to Claude on your
own Anthropic key. The app takes the first provider it can reach, in a fixed
order, and does not ask first. That is not a footnote, and there is no setting in
the app that changes it.</p>

<div class="box warn">
<strong>Why this page does not say "nothing leaves your machine"</strong>
<p>The homepage used to carry that as a badge. It was removed because it was not
true, and it is still not true — not even with Outlier running. Two fetches go
out over the network whichever provider you end up on: the crawl of the site you
typed, and, if you give the ad a destination URL, a fetch of that page. Both are
aimed at sites you named yourself, and neither reaches us. What the model then
sees is a separate question, and the table below answers it.</p>
<p>The claim that does hold, and only while Outlier is the provider that
answered, is the narrower one the app itself makes: <strong>nothing about your
product leaves this Mac.</strong> When Outlier is not the one answering, the
harvested text, your product details, every draft ad and the landing page's text
go to a model vendor on your own key, and the app makes that choice without
asking you.</p>
<p style="margin-bottom:0"><strong>Outlier is also made by {COMPANY}.</strong> The
app ranks it first because it runs locally and costs nothing per run, and you are
entitled to know we have an interest in you using it before you take the
recommendation.</p>
</div>

<h2>Where each thing actually goes</h2>
<p>Read this as the list of destinations, in the order a run reaches them.</p>
<table>
<thead><tr><th>What</th><th>Where it goes</th><th>Kept how long</th></tr></thead>
<tbody>
<tr><td><strong>The website you point it at</strong></td>
<td>Fetched directly by your Mac, at most 25 pages. It reads that site's
<code>robots.txt</code> and skips links that <em>Googlebot</em> would be told to
skip — that is the rule set it follows, because it asks the file about Googlebot
rather than about itself — and it does not apply that check to the address you
typed or to URLs listed in the sitemap. It leaves a quarter of a second between
requests and backs off when a site says it is being asked too often; it does not
read <code>Crawl-delay</code>. It sends a Chrome user-agent string with
<code>AdPlaybook/1.0</code> appended, so a site owner reading their logs closely
can tell what it was, but it does not present itself as a bot to anything that
only checks the prefix. Certificates are not verified on these fetches, because a
broken certificate is itself worth reporting — on a hostile network that means
what it reads could have been tampered with.</td>
<td>In memory for the run</td></tr>
<tr><td><strong>The landing page you point the ad at</strong></td>
<td>Fetched by your Mac, following redirects wherever they lead, including onto a
site you did not name. Its title, headings, calls to action and first 3,000
characters of visible text are then sent to whichever provider is doing the
writing, so the ad's promises can be checked against the page. Unlike the crawl,
this fetch does not read that site's <code>robots.txt</code>, and it still
identifies itself with a user-agent left over from the crawler this was built
from (<code>Docket-SEO-Audit/1.0</code>). Both are bugs and both are on the list.
Leave the destination field empty and none of it happens — and the app reports
the check as skipped rather than as passed.</td>
<td>The fetch itself, in memory for the run. What was sent onward is with the
provider — the row below</td></tr>
<tr><td><strong>The text it harvested, your product details, every draft ad, and
the landing page's text</strong></td>
<td>To exactly one provider, resolved once at the start of the run and used for
all of it. <strong>Outlier</strong> — <code>http://127.0.0.1</code>, this Mac,
nothing over the internet. Or <strong>Claude (Anthropic)</strong>, over the
internet, authenticated with your key; what Anthropic then does with it is
governed by Anthropic's terms and privacy policy, not ours. <strong>ChatGPT
(OpenAI)</strong> is a third option in the code that the app as installed cannot
reach — see the box below. Which one you get is settled by your machine, not by
the picker.</td>
<td>On Outlier it never leaves this Mac; how long Outlier itself then keeps it is
Outlier's business, not ours. On Claude, ask Anthropic — we cannot see it and
cannot speak for them</td></tr>
<tr><td><strong>Your API key</strong></td>
<td>Written to a file on your Mac. The Anthropic key is read back and sent to
Anthropic when a run uses it. A key you enter for ChatGPT is written and read by
nothing at all, so it is sent nowhere, including to OpenAI — see the box below.
Never to us, never to a provider it does not belong to, never into a log line.</td>
<td>Until you delete the file</td></tr>
<tr><td><strong>The brief, the strategy scores, the campaign, the evidence
receipt, the exports</strong></td>
<td>Nowhere. They are held in the app's memory while it runs.</td>
<td>Gone when you quit, unless you saved a file</td></tr>
<tr><td><strong>Anything at all, to {COMPANY}</strong></td>
<td>Never. There is no server of ours for it to reach, no analytics in the app,
no crash reporting, and no licence check that would phone home.</td>
<td>—</td></tr>
</tbody>
</table>

<div class="box warn">
<strong>The provider picker still does not decide anything</strong>
<p>If any provider is already usable on your Mac you never see this screen — the
app goes straight to the start screen and uses that provider, and you reach the
list only through the settings gear. When you do see it, the app lists three
providers and marks Outlier as recommended because Outlier runs on your Mac. In
<strong>{VERSION_TAG} — the build the Download button serves — choosing one does not
change where the run goes.</strong> The button moves you to the next screen and
records nothing.</p>
<p>The run asks the machine instead, in this order. <strong>Outlier</strong>, if
it is both answering on <code>127.0.0.1</code> and has issued a local key this
app can read from <code>~/.outlier/openai_api.json</code> — a running Outlier
with no key in that file is skipped, and the provider screen says "ready" next to
it only when both hold. Otherwise <strong>ChatGPT</strong>, if
<code>OPENAI_API_KEY</code> is set in the environment the app inherits; nothing
in the app sets it and the ChatGPT box in Settings cannot produce it, so unless
you have set that variable yourself for the whole login session, this option is
unreachable. Otherwise <strong>Claude</strong>, if an Anthropic key is on the
machine. Otherwise it stops and names each one it checked and why it could not
use it.</p>
<p>That is a defect, not a policy, and it has a second half worth stating
plainly: <strong>a key you paste into the ChatGPT box is saved and then never
read.</strong> It is written to <code>~/.config/adkit/openai.key</code> and
nothing loads it back. So the practical destination set for the app as shipped is
Outlier or Claude: with Outlier not answering, the run goes to Claude if you have
an Anthropic key and refuses to start if you do not.</p>
<p>The app also does not tell you which one it chose. Nothing names the provider
until the first cost line appears — after the first model call has already
happened — and on Claude that line shows the cost without the vendor's name. The
guide, the evidence receipt and the exports do not record it either. If you need
that in writing for a compliance file, ask.</p>
<p style="margin-bottom:0">Until this page says otherwise, do not treat the
picker as a privacy control. If a run must stay on this Mac, check the provider
screen says "ready" next to Outlier before you start it. If a run must not reach
Anthropic, remove <code>ANTHROPIC_API_KEY</code> from the environment and delete
<code>~/.config/adkit/key</code> (or <code>$XDG_CONFIG_HOME/adkit/key</code>).
Deleting <code>openai.key</code> changes nothing, because that file is not what
the app reads. Removing the key is the only control that actually works.</p>
</div>

<h2>What it writes to your Mac, and exactly where</h2>
<ul>
<li><code>~/.config/adkit/key</code> — your Anthropic key, created with
owner-only permissions (<code>0600</code>). If <code>XDG_CONFIG_HOME</code> is
set, that path is used instead.</li>
<li><code>~/.config/adkit/openai.key</code> — written with the same permissions
when you enter a ChatGPT key, and read by nothing. Always under your home
directory even when <code>XDG_CONFIG_HOME</code> is set, unlike the file above.
Delete it; it does nothing.</li>
<li><code>~/.outlier/openai_api.json</code> — <em>read</em>, never written. That
file belongs to Outlier; the app reads it to find the port Outlier is listening
on and the local key it issued. It also checks an <code>OUTLIER_PORT</code>
variable and, failing both, tries a short range of loopback ports. All of that
stays on this Mac.</li>
<li><code>~/Library/WebKit/app.adplaybook.desktop/</code> — created by the macOS
web view the window is built from. The app stores nothing in it; macOS does.</li>
<li>Anything you explicitly export or save, wherever you chose to save it.</li>
</ul>
<p>That is the complete list. Deleting those files and the app removes
everything it put on the machine.</p>

<h2>This website</h2>
<p>These pages are static files served by GitHub Pages. There are no cookies, no
tag manager, no pixel, no embedded fonts and no form to submit. We set nothing in
your browser and we cannot see who you are.</p>
<p>There are <strong>two</strong> scripts. This page once claimed there were
none, then said one; each time it was corrected the same day the claim stopped
being true, and this is the third such correction rather than a rewrite of
history.</p>
<p>The first is <a href="https://plausible.io/privacy" rel="nofollow">Plausible</a>,
which counts page views without cookies and without collecting anything that
identifies a visitor — no cookie, no device fingerprint, no cross-site profile,
and nothing we could use to recognise you on a return visit. It tells us how many
people read a page, not who.</p>
<p>The second is <a href="https://usesled.com" rel="nofollow">Sled</a>, which
credits the right person when somebody recommends this app. It is conditional and
that distinction is the whole point: it sets a single <code>ta_ref</code> cookie
<strong>only</strong> if you arrived through an affiliate link. Arrive any other
way — a search result, a bookmark, a link from us — and it sets nothing at all. It
records which affiliate sent a visit, never who the visitor is.</p>
<p>View the source of any page and those two scripts are what you will find; there
is nothing else.</p>
<p>Two things are true anyway and you should know them:</p>
<ul>
<li><strong>GitHub serves the site and the download.</strong> Fetching a page or
the DMG is an ordinary HTTP request to GitHub's servers, which receive your IP
address the way any web host does. GitHub's privacy statement governs that.</li>
<li><strong>The domain is verified in Google Search Console.</strong> That shows
us aggregate search queries and click counts for the site. It does not identify
anyone and we cannot use it to.</li>
</ul>

<h2>Your rights, stated honestly</h2>
<p>Access, correction, deletion and portability all assume someone is holding
your data. We are not. There is no database, no mailing list, no customer
record, and no copy of anything the app produced — so a request to see, correct
or delete what we hold has the same answer every time, which is that there is
nothing there.</p>
<p>Where your data may exist — if the run reached a cloud provider rather than
Outlier on your own Mac — is with that provider, under your own account with
them, and with GitHub as the host of this site. Those requests go to them. If it
would help to have that in writing from us for a compliance file, ask and you
will get it.</p>

<div class="box">
<strong>What this page does not cover</strong>
<p>It describes {VERSION_TAG}, dated {EFFECTIVE}. It does not describe any future build,
and it does not describe a paid version, because there is not one — see
<a href="/terms/">the terms</a>. If a payment mechanism, an account, a licence
key or a server ever exists, this page changes before that ships, not after.</p>
<p>It also cannot tell you what your own run will do. Where the writing happens
depends on what is running and which keys are on your Mac at the moment you press
go, and this page cannot see that. It can only tell you the order the app checks
in and what each outcome means, which is what it does above.</p>
<p style="margin-bottom:0">Listed rather than left blank, for the same reason
the spec pages list what could not be verified: a policy with no gaps is either
complete or hiding something, and from the outside those look identical.</p>
</div>

<h2>Changes, and how to reach us</h2>
<p>The date at the top of this page is the date its text last changed, set by
hand. It does not move when the site is rebuilt.</p>
<p>Questions about any of this go to
<a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a>, or see
<a href="/contact/">the contact page</a> for who is on the other end.</p>
<p><a class="btn ghost" href="/terms/">Terms</a>
<a class="btn ghost" href="/contact/">Contact</a></p>
</article>
"""
    page(path="/privacy/",
         title=f"Privacy — what {BRAND} sends, and where | {BRAND}",
         description=desc, body=body, modified=EFFECTIVE)


# ---------------------------------------------------------------------------
# /terms/
# ---------------------------------------------------------------------------

def _terms(page: Callable) -> None:
    desc = ("The terms for using AdPlaybook: who publishes it, what the licence "
            "is, who is responsible for the ads it drafts, and how refunds work.")

    body = f"""{DRAFT_NOTE}
<article>
<p class="crumb">Terms</p>
<h1>Terms of use</h1>
<p class="lede">{esc(desc)}</p>

<div class="box ok">
<p style="margin:0"><span class="pill checked">last changed {TERMS_EFFECTIVE}</span>
These cover the desktop app and this website. They are short because the
product is small: there is no account to close, no subscription to cancel and
no data of yours for us to lose.</p>
</div>

<h2>Who you are dealing with</h2>
<p>{BRAND} is published by <strong>{COMPANY}</strong>, {CITY_STATE}. "We" and
"us" below mean that company. "You" means whoever installed the app.</p>

<div class="box">
<strong>Why the signature says a person and this page says a company</strong>
<p style="margin-bottom:0">If you check the download's signature you will see
<code>Developer ID Application: MATTHEW BENJAMIN-LEE KERR (9N3Z6J63T4)</code>.
Apple issues a Developer ID either to a named individual or to an organisation,
and this build carries the individual's. He owns {COMPANY_PLAIN}. Same person,
two registrations — flagged here rather than left for you to wonder about,
because a signature that does not match the publisher is exactly the sort of
thing worth being suspicious of.</p>
</div>

<h2>What you get, and how you get it</h2>
<p>A macOS application for Apple Silicon, delivered as a signed and notarised
disk image from <a href="{RELEASES}">the releases page</a>. The download is the
whole application — there is no separate paid build, no account to create and
no server to sign in to.</p>
<p>If you buy a licence, Polar emails you a key. You paste it into the app once;
the app asks Polar whether the key is valid and stores that answer at
<code>~/.config/adkit/licence.json</code>. It re-asks at most once a day, and if
your machine cannot reach Polar an already-valid licence keeps working for 14
days before it stops. That is the only network call licensing makes, and it
carries the key and nothing else.</p>

<h2>What it costs</h2>
<p><strong>Free on one website. ${PRICE_USD} once for unlimited websites</strong> —
paid once, not a subscription, with no renewal and no expiry. There is no trial
to run out, because the free tier is not a trial.</p>
<p>Payment is taken by <strong>Polar</strong>, who are the merchant of record:
your card statement will show Polar rather than us, they issue the receipt and
handle sales tax and VAT, and they are the only party who ever sees your card.
The one place to buy is the checkout linked from this site
(<code>buy.polar.sh</code>). We do not sell {BRAND} through app stores, resellers
or key marketplaces, so a key offered anywhere else did not come from us and we
cannot support or honour it.</p>
<p>Free is not the same as costless. The app calls a model on every generation
and you pay that bill directly to your provider, never to us. Which provider that
is depends on what your Mac can reach, not on what you pick — see the box below —
so whether a run costs anything is not something you choose either. If Outlier is
answering locally it is used first and the run costs nothing at all; if it is not,
the run goes to a metered provider on your own key without asking. What a metered
run costs depends on the size of your site and the rates in force at the time, so
we do not publish a figure we cannot stand behind. The app shows the running cost
as it goes rather than presenting a total at the end.</p>

<h2>Refunds and cancellation</h2>
<p>If AdPlaybook does not do what you need, email us within <strong>30 days of
purchase</strong> and we will refund you in full. You do not need to give a
reason. Refunds go to the original payment method only and typically appear
within 5&ndash;10 business days.</p>
<p><strong>Try it before you buy it.</strong> AdPlaybook is free forever on one
website. We would rather you confirm it does what you need than rely on a refund
afterwards &mdash; and if the free tier does not convince you, the paid version
very likely will not either.</p>
<p><strong>One refund per customer.</strong> We refund one purchase per person.
If you buy again after a refund, that purchase is final. This is not aimed at
anyone acting in good faith; it exists because a policy with no limit is a policy
that gets automated against.</p>
<p><strong>After a refund</strong> your licence is deactivated and paid features
stop working. Anything you have already produced with AdPlaybook remains yours to
keep and to use commercially. We do not ask you to delete work.</p>
<p><strong>Purchases made through an affiliate link.</strong> Affiliates earn
commission on sales they refer, and commission is held until the refund window
closes. We reserve the right to decline a refund, and to withhold the related
commission, where a purchase and its refund appear designed to extract commission
rather than to try the product. Ordinary refunds are unaffected and we will not
ask you to justify one.</p>
<p><strong>UK and EU customers.</strong> You normally have a 14-day right to
cancel a purchase of digital content. Because AdPlaybook is supplied immediately
on purchase, you are asked at checkout to acknowledge that supply begins right
away and that you therefore lose that statutory cancellation right once it does.
The 30-day policy above is offered voluntarily and is more generous than the
statutory minimum, so in practice you are not worse off. Nothing here removes
rights you have under mandatory consumer law where you live.</p>
<p><strong>Chargebacks.</strong> Please contact us before raising one. We will
almost certainly just refund you, and it is faster for both of us.</p>
<p>If that ever changes, this section is rewritten and dated <em>before</em> a
paid build ships, not after.</p>

<h2>The licence</h2>
<p>You get a non-exclusive, non-transferable, revocable licence to install and
run {BRAND} on Macs you control, for your own advertising or your clients'. It
costs nothing and it is not exclusive to you.</p>
<p>What it does not include: redistributing a modified build under the {BRAND}
name, presenting the app as your own product, or removing the notices that let
someone verify where the build came from. The name and the site's contents stay
ours.</p>

<h2>What it produces is a draft, and you are the advertiser</h2>
<p>This is the clause that matters. {BRAND} writes a campaign, traces every
factual claim to a line on your own site, blocks the ones it cannot trace, and
checks the result against each platform's published limits. None of that makes
it right, and none of it transfers responsibility.</p>
<ul>
<li><strong>It is not legal advice.</strong> The compliance pre-flight lists
obligations that commonly attach to what you sell, with a source for each. It is
not exhaustive, it cannot know your jurisdiction, and it does not know your
business.</li>
<li><strong>It cannot check what it could not read.</strong> A page behind a
login, a claim that lives only in a PDF, a landing page you did not give it —
these produce silence, and silence is not a pass.</li>
<li><strong>A traceable claim is not a true one.</strong> The claim gate proves
a statement appears on your site. Whether your site is right is your problem,
and it was before you installed this.</li>
<li><strong>Whoever signs the ad off carries the liability for it.</strong> That
is the person the evidence receipt is written for. If nobody at your end is
qualified to sign it, the tool has not solved that.</li>
</ul>
<p>You own what it drafts for you. We never see it, so we could not claim it if
we wanted to. Where a model provider generated part of it, that provider's terms
govern their side of it.</p>

<h2>How you may use it</h2>
<p>Two rules, both about other people:</p>
<ul>
<li><strong>Only crawl what you are entitled to crawl.</strong> The app reads
whatever URL you hand it. It obeys <code>robots.txt</code> and rate limits, but
it cannot know whether you have the right to point it at a given site. That
judgement is yours.</li>
<li><strong>Do not use it to build advertising that is unlawful</strong> where
you are running it — including in the special categories the app itself warns
you about.</li>
</ul>

<h2>No warranty, two known defects, and one correction</h2>
<p>{BRAND} is provided <strong>as is</strong>, with no warranty of any kind: not
of merchantability, not of fitness for a particular purpose, not that it will be
uninterrupted or error-free. It is a free tool made by one person.</p>
<div class="box warn">
<p>Two things we already know about the build behind the Download button and
would rather you heard from us. <strong>In {VERSION_TAG} the provider picker still does
not change where a run goes.</strong> The interface offers Outlier, ChatGPT and
Claude and recommends Outlier as the local option, but the button records
nothing: the run uses whichever provider your machine can actually reach, in that
order. And <strong>a key entered for ChatGPT is saved but never used</strong> —
it is written to disk and nothing reads it back, so that option cannot be reached
from the interface at all.</p>
<p style="margin:0">We also owe a correction about <strong>v0.1.5</strong>, the
build this site offered until now. These terms and the privacy page used to say
it sent every run to Anthropic regardless of what you picked. That was wrong, and
wrong in the direction of overstating what left your machine: v0.1.5 could not
complete a single campaign, because every model call raised a
<code>TypeError</code> on the way in, before any request was made. Nothing you
typed reached a model vendor, because it never got that far — the only thing that
left your Mac was the crawl of the site you pointed it at.
<a href="/privacy/">The privacy page</a> sets out what {VERSION_TAG} sends, and to
whom.</p>
</div>

<h2>What we owe you if it goes wrong</h2>
<p>To the fullest extent Michigan law allows, {COMPANY} is not liable for
indirect, incidental, special or consequential damages, for lost profits, or for
advertising spend — including a campaign that was rejected, ran badly, or should
not have run. Our total liability for any claim is capped at what you paid for
{BRAND}, which is nothing.</p>
<p>Some liability cannot be excluded by contract, and this does not try to:
nothing here limits liability for fraud, for fraudulent misrepresentation, or
for anything else Michigan law does not permit to be limited.</p>

<h2>Governing law</h2>
<p>These terms are governed by the laws of the State of Michigan, without regard
to its conflict-of-laws rules. Any dispute goes to the state or federal courts
located in Kent County, Michigan, and both sides submit to that.</p>

<h2>Changes, and ending it</h2>
<p>We can change these terms; the date at the top is when the text last changed
and it is set by hand. A change that affects what the software does or costs
will be dated before it ships. Continuing to use the app after a change means
you accept the current version — and since the app runs entirely on your
machine, an older build you already have keeps working regardless.</p>
<p>You can stop at any time by deleting the app. We can stop distributing it at
any time, which does not take back the copy you have.</p>

<h2>Reaching a person</h2>
<p><a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a>, or see
<a href="/contact/">the contact page</a>.</p>
<p><a class="btn ghost" href="/privacy/">Privacy</a>
<a class="btn ghost" href="/contact/">Contact</a></p>
</article>
"""
    page(path="/terms/", title=f"Terms of use | {BRAND}",
         description=desc, body=body, modified=EFFECTIVE)


# ---------------------------------------------------------------------------
# /contact/
# ---------------------------------------------------------------------------

def _contact(page: Callable) -> None:
    desc = (f"Who publishes {BRAND}, where they are, and how to reach a person "
            "about a bug, a security problem or a question about the terms.")

    body = f"""{DRAFT_NOTE}
<article>
<p class="crumb">Contact</p>
<h1>Who is behind this</h1>
<p class="lede">{esc(desc)}</p>

<h2>The publisher</h2>
<p><strong>{COMPANY}</strong><br>
{_address_html()}</p>
<p>{BRAND} is built and maintained by one person. There is no support desk and
no ticket queue, so the honest answer on response times is that mail gets read
and answered by a human, usually within a few days, and there is no promise
beyond that.</p>

<div class="box">
<strong>Email</strong>
<p style="margin-bottom:0"><a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a>
— for anything: bugs, security, the terms, the privacy page, or telling us a
number on this site is wrong.</p>
</div>

<div class="box warn">
<p style="margin:0">There is deliberately no <code>@adplaybook.app</code>
address. The domain has no mail records, so an address on it would bounce
silently, and an address that bounces is worse than one that looks informal.
When there is a mailbox on the domain, this page will say so.</p>
</div>

<h2>Bugs, and the thing that helps most</h2>
<p>Bugs can go to <a href="{ISSUES}">the issue tracker</a> or to the address
above. What makes a report actionable here is unusual, because the app keeps
nothing: we have no copy of your run, no log on a server, and no way to
reproduce what you saw from our end. So please include the URL you pointed it
at, the version from the title bar, which provider the app showed as "ready" on
the provider screen, and what the app said verbatim.</p>
<p>If a number on this site is wrong, that is worth reporting on its own. Every
figure here is supposed to carry the source it came from and the date it was
read, and a wrong one is a bug in the same sense the app is.</p>

<h2>Security</h2>
<p>If you have found something that puts a user's API key or their machine at
risk, email it rather than filing it publicly, and say clearly in the subject
line that it is a security report. You will get an acknowledgement. Include what
you did, what happened, and the build you did it on.</p>

<h2>What we cannot help with</h2>
<ul>
<li><strong>Recovering a run.</strong> Nothing is stored anywhere we can reach —
see <a href="/privacy/">what the app keeps and where</a>. If it is gone from
your machine, it is gone.</li>
<li><strong>Legal advice on your advertising.</strong> The app lists the
obligations that commonly attach to what you sell, with a source for each, and
that is the limit of it. Whoever signs your ads off should be qualified to.</li>
<li><strong>Billing.</strong> We never see your card and cannot look up your
payment. Polar is the merchant of record for every {BRAND} licence — receipts,
invoices, tax and card problems are theirs, and a refund we approve is still
paid out by them. Email us anyway if something has gone wrong and we will tell
you exactly who to ask. Model usage is billed to you by your provider directly
and never passes through us at all.</li>
</ul>

<h2>The rest of it</h2>
<p><a href="/privacy/">What this sends and where</a> ·
<a href="/terms/">Terms of use</a> · <a href="{RELEASES}">All releases</a></p>
<p><a class="btn" href="mailto:{CONTACT_EMAIL}">Email us</a>
<a class="btn ghost" href="/specs/">See the ad specs</a></p>
</article>
"""
    page(path="/contact/", title=f"Contact and publisher details | {BRAND}",
         description=desc, body=body, modified=EFFECTIVE)
