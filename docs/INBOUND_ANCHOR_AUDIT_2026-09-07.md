# Inbound anchors per page, and why the linking order should not be done

**Measured 2026-09-07 across all 58 HTML pages.** The standing order was to add hub links to
the 15 "discovered – not indexed" pages. The 2026-09-07 20:35Z addendum said to count first,
because the same hypothesis had already been measured and falsified on crispvideo.app, where
the never-crawled hubs turned out to be the best-linked pages on the site.

**It does not hold here either. Do not do the linking work.**

## Method

Every `<a href>` in every page, with the traps the addendum names and one it does not:

- **absolute hrefs counted** — `https://adplaybook.app/x/` is normalised to `/x/`. Matching only
  root-relative hrefs is how an orphan sweep on a sibling site reported 146 orphans of 248 when
  the real answer was 6.
- **canonicals excluded by construction** — the pattern matches `<a `, and a canonical is a
  `<link>`, so it can never be counted. Excluded because of what is matched, not by filtering
  afterwards.
- **self-links excluded** — 14 of them. A page linking to itself is not inbound.
- **vacuity guard** — the count asserts a non-zero total across the site before reporting.
  A silent zero from a too-narrow pattern reads exactly like a clean result.

## Result

    pages                        58
    internal anchors counted   1087
    orphans (0 inbound)           1   /thank-you/  — correctly so, it is a post-conversion page
    median inbound                4
    median page weight        3,167 chars

Least-linked real pages:

| page | inbound | weight |
|---|---|---|
| /specs/microsoft-advertising/ | 2 | 4,118 |
| /specs/reddit/ | 2 | 3,128 |
| /specs/google/ | 3 | 3,680 |
| /how-to/stop-ad-copy-reading-like-ai/ | 3 | 3,276 |
| /how-to/split-test-ads-that-actually-say-something/ | 3 | 3,158 |
| /how-to/fix-an-ad-that-is-not-delivering/ | 3 | 3,531 |

## What it means

**No page on this site is meaningfully under-linked.** The floor is 2 inbound anchors, the
median is 4, and the single orphan is the one page that should be one. There is no page that
Google could reach only with difficulty, so "add hub links" cannot be the thing standing
between these URLs and the index.

Per the addendum's own rule — *link only if the count says the pages are under-linked;
otherwise the lever is the page* — **the lever is the page.** The order is closed as measured,
not done.

## What this does not settle

The exact 15 "discovered – not indexed" URLs are not listed in the orders, so this is a
distribution over all 58 pages rather than a comparison between the indexed and not-indexed
sets. If that list becomes available the weight comparison is worth running, since content
weight was the factor that correlated on crispvideo.app. What the distribution already rules
out is the linking remedy: a floor of 2 leaves no room for "under-linked" to be the cause.

## A recommendation I withdrew, and why it is worth recording

I first wrote that `/specs/microsoft-advertising/` — 2 inbound, and the page built for this
site's two highest-impression queries — deserved a link from the truncation article on its own
merits. Then I checked which two anchors those were:

    learn/ad-copy-truncation-vs-hard-limits/index.html   "Microsoft Advertising (Bing)"
    specs/index.html                                     "Microsoft Advertising (Bing) character limit"

It already has exactly that link, plus the hub. The orders said so and I proposed the work
anyway without looking. **A count of 2 is not evidence of under-linking when 2 is every page
that should link to it.** That is the same failure as recommending a fix without reading the
rule it applies to, and it is why "verify the claim before acting on it" applies to my own
recommendations and not only to other people's.
