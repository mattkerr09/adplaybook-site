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
* what v0.1.5 does     `git show dac347a:backend/adkit/server.py:53,329`
* signing identity     `codesign -dvvv` on `dist/AdPlaybook-0.1.5-arm64.dmg`
* zero MX records      `dig +short MX adplaybook.app` -> empty, 2026-08-11

The one that matters most is `dac347a`. In the build behind the Download
button, `run.client = Client()` — the Anthropic client, unconditionally. The
provider picker is in the API surface but not in the run path. So the honest
privacy statement for the *shipped* build is "it goes to Anthropic", not "it
depends which provider you chose", and this page says that.
"""

from __future__ import annotations

import html
from typing import Any, Callable

BRAND = "AdPlaybook"
COMPANY = "Kerr &amp; Company LLC"
COMPANY_PLAIN = "Kerr & Company LLC"

#: Bumped by hand when the text changes, never generated from `date.today()`.
#: A policy whose "last updated" moves every time the site is rebuilt is
#: telling the reader something untrue about when it was last thought about.
EFFECTIVE = "2026-08-11"

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
            "the one step that does leave your Mac.")

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
<p>One step is different, and it is the one that matters. In the build you can
download today, the writing is done by <strong>Anthropic's API, using your own
key</strong> — so the text harvested from your site, your product details and
every draft ad are sent to Anthropic. That is not a footnote and it is not
optional in this build.</p>

<div class="box warn">
<strong>A correction to the homepage</strong>
<p>The homepage carries a badge reading "Nothing leaves your machine". That is
true of the crawl, true of your key, and true of everything the app stores. It
is <em>not</em> true of the generation step in v0.1.5, which sends text to
Anthropic. The badge overstates it, the badge is wrong, and this page is the
accurate statement until the badge is corrected.</p>
</div>

<h2>Where each thing actually goes</h2>
<p>Read this as the list of destinations, in the order a run reaches them.</p>
<table>
<thead><tr><th>What</th><th>Where it goes</th><th>Kept how long</th></tr></thead>
<tbody>
<tr><td><strong>The website you point it at</strong></td>
<td>Fetched directly by your Mac. At most 25 pages, obeying that site's
<code>robots.txt</code> and its <code>Crawl-delay</code>, with the crawler
identifying itself in the User-Agent rather than pretending to be a browser.</td>
<td>In memory for the run</td></tr>
<tr><td><strong>The text it harvested, your product details, and every draft
ad</strong></td>
<td><strong>Anthropic's API</strong>, over the internet, authenticated with your
key. What Anthropic then does with it is governed by Anthropic's terms and
privacy policy, not ours.</td>
<td>Ask Anthropic — we cannot see it and cannot speak for them</td></tr>
<tr><td><strong>Your API key</strong></td>
<td>Written to a file on your Mac and sent only to the provider it belongs to.
Never to us, never to the other providers, never into a log line.</td>
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
<strong>The provider picker does not work in this build</strong>
<p>The app lists three providers and recommends Outlier because Outlier runs on
your Mac, which would mean nothing leaves it at all. In <strong>v0.1.5 —
the build the Download button serves — choosing a provider does not change
where the run goes.</strong> The run path calls Anthropic unconditionally.</p>
<p>That is a defect, not a policy. The current source picks whichever provider
is actually usable, Outlier first, so a later build will behave the way the
interface describes. Until that build ships and this page changes, treat every
run as going to Anthropic, and do not point it at anything you would not send
there.</p>
</div>

<h2>What it writes to your Mac, and exactly where</h2>
<ul>
<li><code>~/.config/adkit/key</code> — your Anthropic key, created with
owner-only permissions (<code>0600</code>). If <code>XDG_CONFIG_HOME</code> is
set, that path is used instead.</li>
<li><code>~/.config/adkit/&lt;provider&gt;.key</code> — the same, for any other
provider you add a key for.</li>
<li><code>~/.outlier/openai_api.json</code> — <em>read</em>, never written. That
file belongs to Outlier; the app reads it only to find the port Outlier is
listening on and the local key it issued.</li>
<li>Anything you explicitly export or save, wherever you chose to save it.</li>
</ul>
<p>That is the complete list. Deleting those files and the app removes
everything it put on the machine.</p>

<h2>This website</h2>
<p>These pages are static files served by GitHub Pages. There are no cookies, no
analytics script, no tag manager, no pixel, no embedded fonts and no form to
submit — view the source of any page and there is nothing to find. We set
nothing in your browser and we cannot see who you are.</p>
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
<p>Where your data does exist is with the model provider you used, under your
own account with them, and with GitHub as the host of this site. Those requests
go to them. If it would help to have that in writing from us for a compliance
file, ask and you will get it.</p>

<div class="box">
<strong>What this page does not cover</strong>
<p>It describes v0.1.5, dated {EFFECTIVE}. It does not describe any future build,
and it does not describe a paid version, because there is not one — see
<a href="/terms/">the terms</a>. If a payment mechanism, an account, a licence
key or a server ever exists, this page changes before that ships, not after.</p>
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
            "is, who is responsible for the ads it drafts, and why there is "
            "nothing to refund.")

    body = f"""{DRAFT_NOTE}
<article>
<p class="crumb">Terms</p>
<h1>Terms of use</h1>
<p class="lede">{esc(desc)}</p>

<div class="box ok">
<p style="margin:0"><span class="pill checked">last changed {EFFECTIVE}</span>
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
disk image from <a href="{RELEASES}">the releases page</a>. Downloading it is
the entire delivery. There is no licence key to enter, no activation step, no
account to create and no server to sign in to — if the app opens, you have
everything there is.</p>

<h2>What it costs</h2>
<p><strong>Nothing, and it is not for sale.</strong> There is no price, no
checkout, no trial, no subscription and no payment mechanism anywhere in this
product or on this site. If any page anywhere asks you to pay for {BRAND}, it is
not us and you should not pay it.</p>
<p>Free is not the same as costless. The app calls a model on every generation
and you pay that bill directly to your provider, never to us. What a run costs
depends on the provider you choose, the size of your site and the rates in force
at the time, so we do not publish a figure we cannot stand behind. The app shows
the running cost as it goes rather than presenting a total at the end. Running
it against a local model instead costs nothing at all.</p>

<h2>Refunds and cancellation</h2>
<p>There is nothing to refund and nothing to cancel. No money has been taken
from anyone, and there is no mechanism by which it could be. Stopping is
dragging the app to the trash.</p>
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

<h2>No warranty, and one known defect</h2>
<p>{BRAND} is provided <strong>as is</strong>, with no warranty of any kind: not
of merchantability, not of fitness for a particular purpose, not that it will be
uninterrupted or error-free. It is a free tool made by one person.</p>
<div class="box warn">
<p style="margin:0">One thing we already know about the build behind the
Download button and would rather you heard from us: <strong>in v0.1.5 the
provider picker does not change where a run goes.</strong> The interface offers
Outlier, ChatGPT and Claude and recommends Outlier as the local option; the run
path calls Anthropic regardless. If you installed it expecting nothing to leave
the machine, it did. <a href="/privacy/">The privacy page</a> sets out what was
sent.</p>
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
at, the version from the title bar, which provider was configured, and what the
app said verbatim.</p>
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
<li><strong>Billing.</strong> There is no billing. {BRAND} is not for sale and
takes no payments — <a href="/terms/">the terms</a> set that out. Model usage is
billed to you by your provider directly.</li>
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
