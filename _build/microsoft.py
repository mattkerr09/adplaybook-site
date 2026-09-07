"""/specs/microsoft-advertising/ — Bing Ads character limits.

WHY THIS PAGE EXISTS, and it is the only page on the site built from a search
query rather than from the app. Search Console, 2026-09-07: the site's two
biggest queries are "bing ads character limits" (50 impressions) and "bing ad
character limit" (32) — 82 of 558 total — and there was no Bing page at all.

WHY IT IS NOT A GENERATED /specs/ PAGE. Every other platform page is rendered
from `~/ad maker app/backend/adkit/platforms/*.json`, and the app carries eight
platforms. Microsoft Advertising is not one of them. Adding a JSON there would
make the APP claim it builds Microsoft campaigns — placements, objectives,
exports, compliance rules and all — which is a product decision in another
session's repo, not an SEO fix. So this is a reference page that says plainly
what the app does and does not do.

EVERY NUMBER IS QUOTED FROM MICROSOFT'S OWN API REFERENCE, read on the date
below. Nothing here is remembered, inferred from Google's limits, or rounded.
The two documents:

    https://learn.microsoft.com/en-us/advertising/campaign-management-service/responsivesearchad
    https://learn.microsoft.com/en-us/advertising/campaign-management-service/responsivead

Both carry ms.date 2024-11-13 and were served with updated_at 2026-09-07.
"""
from __future__ import annotations

READ_ON = "2026-09-07"
RSA_URL = ("https://learn.microsoft.com/en-us/advertising/"
           "campaign-management-service/responsivesearchad")
RA_URL = ("https://learn.microsoft.com/en-us/advertising/"
          "campaign-management-service/responsivead")


def build(page, neighbours, guides) -> None:
    body = f"""
<article>
<p class="crumb"><a href="/specs/">Ad specs</a> / Microsoft Advertising</p>
<h1>Microsoft Advertising (Bing) ad character limits</h1>
<p class="lede">Bing's limits have a second number almost nobody publishes: the
length your text may be when you type it, and the length it may be
<em>after</em> dynamic text is substituted. Exceed the second and the ad does
not truncate — it fails to display.</p>

<h2>What are the character limits for Bing responsive search ads?</h2>
<p>Three to fifteen headlines at 30 characters each, and two to four
descriptions at 90. Those are the limits that apply after any dynamic text is
resolved.</p>
<table><thead><tr><th>Field</th><th>How many</th><th>Limit you type</th>
<th>Limit after substitution</th></tr></thead><tbody>
<tr><td>Headline</td><td>3–15</td><td>1,000</td><td><strong>30</strong></td></tr>
<tr><td>Description</td><td>2–4</td><td>1,000</td><td><strong>90</strong></td></tr>
<tr><td>Path 1</td><td>0–1</td><td>1,000</td><td><strong>15</strong></td></tr>
<tr><td>Path 2</td><td>0–1, needs Path 1</td><td>1,000</td><td><strong>15</strong></td></tr>
<tr><td>Final URL</td><td>up to 10, first used</td><td colspan="2">2,048, protocol counted</td></tr>
</tbody></table>
<p class="note">Read from <a href="{RSA_URL}" rel="nofollow">Microsoft's
ResponsiveSearchAd reference</a> on {READ_ON}. The 1,000-character figure is
the input allowance when the field contains dynamic text strings such as
<code>{{keyword}}</code>; the bold number is what survives.</p>

<h2>Why does my Bing ad fail to display instead of truncating?</h2>
<p>Because Bing treats an over-length result as an error, not as something to
cut. Microsoft's wording is exact: the ad "will fail to display or default text
will be used if the length exceeds 30 characters after dynamic text
substitution occurs."</p>
<p>That is the trap in one sentence. A headline of <code>Save on
{{keyword}}</code> is 18 characters in the box and passes every check you can
run before launch. Substituted against a long search term it can land past 30,
and the result is not a shortened headline — it is your default text, or
nothing.</p>

<h2>Do the limits change for Chinese, Japanese or Korean ads?</h2>
<p>Yes, and they halve. Double-width characters get 15 final characters for a
headline and 45 for a description, from a 500-character input allowance rather
than 1,000.</p>
<p>Microsoft is specific about what counts: "the double-width characters are
determined by the characters you use instead of the character set of the
campaign or ad group language settings," and the list includes emoji. An emoji
in an English headline moves that headline onto the 15-character rule.</p>

<h2>How long can the display URL path be?</h2>
<p>Fifteen final characters each for Path 1 and Path 2 — but the binding
constraint is the total: the domain plus both paths "cannot exceed 67
characters," or 33 for double-width. Path 2 cannot be set without Path 1, a
space inside a path is shown as an underscore, and a forward slash is not
allowed at all.</p>

<h2>What are the limits for Microsoft Audience and multimedia ads?</h2>
<p>A different object with different numbers, which is why a single "Bing
character limit" answer is usually wrong.</p>
<table><thead><tr><th>Field</th><th>How many</th><th>Limit</th></tr></thead><tbody>
<tr><td>Business name</td><td>1</td><td>25</td></tr>
<tr><td>Headline</td><td>1–15</td><td>30 after substitution</td></tr>
<tr><td>Long headline</td><td>1–5</td><td>90</td></tr>
<tr><td>Description</td><td>1–5</td><td>90 after substitution</td></tr>
<tr><td>Text (video ads)</td><td>1</td><td>90</td></tr>
</tbody></table>
<p class="note">Read from <a href="{RA_URL}" rel="nofollow">Microsoft's
ResponsiveAd reference</a> on {READ_ON}.</p>

<h2>Does AdPlaybook build Microsoft Advertising campaigns?</h2>
<p>No. It builds for Google Ads, LinkedIn, Meta, Pinterest, Reddit, TikTok, X
and YouTube — eight platforms, each with its limits read from that platform's
own documentation and carrying the date it was read. Microsoft Advertising is
not among them, and this page is a reference rather than a claim of support.</p>
<p>The <a href="/specs/">ad specs pages</a> cover the eight it does build for,
and <a href="/learn/ad-copy-truncation-vs-hard-limits/">the difference between
a hard limit and a truncation point</a> is the same trap on every platform —
Bing's version is just unusually punishing, because the penalty is a dead ad
rather than an ellipsis.</p>
</article>
"""
    page(
        related=neighbours(guides, "/specs/microsoft-advertising/"),
        path="/specs/microsoft-advertising/",
        title="Microsoft Advertising (Bing) ad character limits (2026) | AdPlaybook",
        description=("Bing responsive search ad limits: 30-character headlines, "
                     "90-character descriptions, and the after-substitution rule "
                     "that makes an over-length ad fail rather than truncate."),
        body=body,
        # TechArticle, so this page gets the dates every other article gets.
        #
        # Shipped once without it and caught it on the live page: no schema
        # means `is_article` is False in render.py, which means no dateline, no
        # <time datetime> and no Open Graph article times — the exact gap
        # closed one commit earlier, reopened by a new page that did not opt in.
        # A fix that only covers the pages existing on the day it lands is not
        # a fix, it is a sweep.
        schema={"@context": "https://schema.org", "@type": "TechArticle",
                "headline": "Microsoft Advertising (Bing) ad character limits"},
    )
