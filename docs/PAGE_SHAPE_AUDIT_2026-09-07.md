# Every page against the truncation article

**Benchmark: `/learn/ad-copy-truncation-vs-hard-limits/`** — the site's highest-impression page
(297). Measurably it does two things: **3 of its 3 real headings are questions**, and it cites
**22 specific numbers** in 2,592 characters. Those are the two axes audited here, because they
are the two the Docket content-shape findings name and the only two that can be counted rather
than judged.

Measured 2026-09-07 across all 58 pages. `/`, `/contact/`, `/privacy/`, `/thank-you/` are
exempt — a contact page has no question to answer and a privacy page should not invent one.

| family | pages | median question-ratio | median numbers | verdict |
|---|---|---|---|---|
| `/vs/` | 1 | 0.00 | 11 | below on headings |
| `/strategies/` | 11 | 0.00 | 5 | **below on both** |
| `/for/` | 11 | 0.00 | 6 | **below on both** |
| `/offline/` | 1 | 0.00 | 20 | below on headings |
| `/specs/` | 10 | 0.37 | 26 | below on headings |
| `/learn/` | 15 | 1.00 | 11 | at benchmark |
| `/how-to/` | 4 | 1.00 | 8 | at benchmark |

## What the table says, including where it contradicted what I expected

`/learn/` (1.00) and `/how-to/` (1.00) are at the benchmark. Those are where five of the site's
six impression-earning pages live, so **order 4 — apply the content shape to the winners first —
is done for them.**

**`/specs/` is NOT done, at 0.37.** I wrote the opposite in a first draft of this file, from
memory of the commit that added question headings to that template (`5f29199`), and the table
I had just generated said otherwise. Ten pages, and fewer than four in ten of their headings
are questions — despite `/specs/` itself being an impression-earning page (46). It is the
highest-value gap on this list precisely because it already earns impressions.

## The gap, in priority order

**1. `/specs/` — 10 pages at 0.37, and already earning.** Highest value: the traffic exists and
the shape does not. Its specifics are the site's strongest (median 26 numbers), so this is
headings only.

**2. `/strategies/` — 11 pages, 0.00 question-ratio, median 5 numbers.** Below on both axes,
uniformly. Cheapest to fix because the family shares a template, but it earns nothing today, so
it is a bet rather than a repair.

**2. `/for/` — audience pages, 1-4 numbers each.** These are the thinnest pages on the site for
specifics. A page for plumbers that names no limit, no floor and no cost is a page an AI engine
has nothing to quote from.

## What this audit does NOT claim

That question marks cause rankings. The two axes are copied from the site's best-performing
page and from Docket's audit; that is a reason to try them, not evidence they are why it wins.
The honest test is the same as everywhere else here: change one family, leave the rest, and
read the console in a fortnight. Nothing on this page should be cited as a result.
